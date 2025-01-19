import threading
from typing import List, Type
from models.v2.shipment import Shipment
from models.v2.ItemInObject import ItemInObject
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v2 import data_provider_v2
from utils.globals import *
from services.v1 import data_provider


class ShipmentService(Base):
    def __init__(
        self,
        data_provider=None,
        is_debug: bool = False,
    ):
        self.is_debug = is_debug
        if data_provider is not None:
            self.data_provider = data_provider
        else:
            self.data_provider = data_provider_v2

        self.db = self.data_provider.fetch_database()
        self.load()

    def get_all_shipments(self) -> List[Shipment]:
        all_shipments = self.db.get_all(Shipment)
        shipment_ids = [shipment.id for shipment in all_shipments]

        with self.db.get_connection() as conn:
            query = f"SELECT item_uid, amount, shipment_id FROM {shipment_items_table} WHERE shipment_id IN ({', '.join(map(str, shipment_ids))})"
            cursor = conn.execute(query)
            all_shipment_items = cursor.fetchall()

        shipment_items_map = {}
        for row in all_shipment_items:
            if row[2] not in shipment_items_map:
                shipment_items_map[row[2]] = []
            shipment_items_map[row[2]].append(
                ItemInObject(item_id=row[0], amount=row[1])
            )
        for i, shipment in enumerate(all_shipments):
            all_shipments[i].items = shipment_items_map.get(shipment.id)

        return all_shipments

    def get_shipments(self) -> List[Shipment]:
        all_shipments = []
        for shipment in self.data:
            if not shipment.is_archived:
                all_shipments.append(shipment)
        return all_shipments

    def get_shipment(self, shipment_id: int) -> Shipment | None:
        for shipment in self.data:
            if shipment.id == shipment_id:
                return shipment

        with self.db.get_connection() as conn:
            query = f"SELECT * FROM {Shipment.table_name()} WHERE id = ?"
            cursor = conn.execute(query, (shipment_id,))
            shipment_row = cursor.fetchone()
            if shipment_row:
                column_names = [desc[0] for desc in cursor.description]
                shipment = dict(zip(column_names, shipment_row))
                query_items = f"SELECT item_uid, amount FROM {shipment_items_table} WHERE shipment_id = {shipment_id}"
                cursor = conn.execute(query_items)
                all_shipment_items = cursor.fetchall()
                shipment["items"] = [
                    ItemInObject(item_id=row[0], amount=row[1])
                    for row in all_shipment_items
                ]
                return Shipment(**shipment)
        return None

    def get_items_in_shipment(self, shipment_id: int) -> List[ItemInObject] | None:
        shipment = self.get_shipment(shipment_id)
        return shipment.items if shipment else None

    def add_shipment(self, shipment: Shipment, background_task=True) -> Shipment:

        if self.has_shipment_archived_entities(shipment):
            return None

        table_name = shipment.table_name()

        shipment.created_at = self.get_timestamp()
        shipment.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(shipment).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection() as conn:
            cursor = conn.execute(insert_sql, values)
            shipment_id = cursor.lastrowid
            shipment.id = shipment_id

            if shipment.items:
                for shipment_items in shipment.items:
                    items_insert_sql = f"""
                    INSERT INTO {shipment_items_table} (shipment_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (shipment_id, shipment_items.item_id, shipment_items.amount),
                    )
        self.data.append(shipment)
        self.save(background_task)
        return shipment

    def update_shipment(
        self, shipment_id: int, shipment: Shipment, background_task=True
    ) -> Shipment:

        current_shipment = self.get_shipment(shipment_id)

        if self.is_shipment_archived(
            shipment_id
        ) is not False or self.has_shipment_archived_entities(
            shipment, current_shipment
        ):
            return None

        table_name = shipment.table_name()
        shipment.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(shipment).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(f"{key} = ?" for key in fields)
        values = tuple(fields.values())

        update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"
        with self.db.get_connection() as conn:
            conn.execute(update_sql, values + (shipment_id,))

            if shipment.items:
                current_shipment_item_ids = {
                    item.item_id for item in current_shipment.items
                }
                for shipment_items in shipment.items:
                    if shipment_items.item_id not in current_shipment_item_ids:
                        items_insert_sql = f"""
                        INSERT INTO {shipment_items_table} (shipment_id, item_uid, amount)
                        VALUES (?, ?, ?)
                        """
                        conn.execute(
                            items_insert_sql,
                            (
                                shipment_id,
                                shipment_items.item_id,
                                shipment_items.amount,
                            ),
                        )
                new_shipment_item_ids = {item.item_id for item in shipment.items}
                for current_item_id in current_shipment_item_ids:
                    if current_item_id not in new_shipment_item_ids:
                        conn.execute(
                            f"DELETE FROM {shipment_items_table} WHERE shipment_id = ? AND item_uid = ?",
                            (shipment_id, current_item_id),
                        )

        for i in range(len(self.data)):
            if self.data[i].id == shipment_id:
                shipment.id = shipment_id
                if shipment.created_at is None:
                    shipment.created_at = self.data[i].created_at
                self.data[i] = shipment
                self.save(background_task)
                break
        return shipment

    def update_items_in_shipment(
        self, shipment_id: int, items: List[ItemInObject]
    ) -> Shipment | None:
        shipment = self.get_shipment(shipment_id)
        updated_shipment = shipment.model_copy()
        updated_shipment.items = items
        if self.has_shipment_archived_entities(shipment, updated_shipment):
            return None

        if shipment:
            items_to_add = []
            for item in items:
                if not self.data_provider.fetch_item_pool().is_item_archived(
                    item.item_id
                ):
                    items_to_add.append(item)
            if len(items_to_add) > 0:
                self.update_inventory_for_items(shipment.items, items_to_add)
                updated_shipment.items = items_to_add
                return self.update_shipment(shipment_id, updated_shipment)
        return None

    def update_inventory_for_shipment(self, item_id, amount_change):
        inventories = (
            self.data_provider.fetch_inventory_pool().get_inventories_for_item(item_id)
        )
        max_inventory = max(inventories, key=lambda z: z.total_ordered, default=None)
        if max_inventory:
            if max_inventory.total_ordered + amount_change >= 0:
                max_inventory.total_ordered += amount_change
                max_inventory.total_expected = (
                    max_inventory.total_on_hand + max_inventory.total_ordered
                )
                self.data_provider.fetch_inventory_pool().update_inventory(
                    max_inventory.id, max_inventory
                )

    def update_inventory_for_items(
        self, current_items: List[ItemInObject], new_items: List[ItemInObject]
    ):
        new_items_dict = {item.item_id: item for item in new_items}
        for current in current_items:
            item_id = current.item_id
            current_amount = current.amount
            if item_id in new_items_dict:
                new_amount = new_items_dict[item_id].amount
                amount_change = new_amount - current_amount
                if amount_change != 0:
                    self.update_inventory_for_shipment(item_id, amount_change)
            else:
                self.update_inventory_for_shipment(item_id, -current_amount)
        current_item_ids = {current.item_id for current in current_items}
        for item in new_items:
            if item.item_id not in current_item_ids:
                self.update_inventory_for_shipment(item.item_id, item.amount)

    def archive_shipment(
        self, shipment_id: int, background_task=True
    ) -> Shipment | None:
        for i in range(len(self.data)):
            if self.data[i].id == shipment_id:
                self.data[i].is_archived = True
                table_name = self.data[i].table_name()
                self.data[i].updated_at = self.get_timestamp()

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"
                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values + (shipment_id,))

                self.save(background_task)
                return self.data[i]
        return None

    def unarchive_shipment(
        self, shipment_id: int, background_task=True
    ) -> Shipment | None:
        for i in range(len(self.data)):
            if self.data[i].id == shipment_id:
                self.data[i].is_archived = False
                table_name = self.data[i].table_name()
                self.data[i].updated_at = self.get_timestamp()

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"
                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values + (shipment_id,))

                self.save(background_task)
                return self.data[i]
        return None

    def save(self, background_task=True):  # pragma: no cover:
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_shipment_pool().save(
                    [shipment.model_dump() for shipment in self.data]
                )

            if background_task:
                threading.Thread(target=call_v1_save_method).start()
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_shipments()

    def has_shipment_archived_entities(
        self, new_shipment: Shipment, old_shipment: Shipment | None = None
    ) -> bool:
        has_archived_entities = False
        if old_shipment is None:
            if new_shipment.is_archived:
                has_archived_entities = True
            elif self.data_provider.fetch_order_pool().is_order_archived(
                new_shipment.order_id
            ):
                has_archived_entities = True
            else:
                for item in new_shipment.items:
                    if self.data_provider.fetch_item_pool().is_item_archived(
                        item.item_id
                    ):
                        has_archived_entities = True
                        break
        else:
            if new_shipment.is_archived and not old_shipment.is_archived:
                has_archived_entities = True
            elif (
                new_shipment.order_id != old_shipment.order_id
                and self.data_provider.fetch_order_pool().is_order_archived(
                    new_shipment.order_id
                )
            ):
                has_archived_entities = True
            else:
                old_item_ids = {item.item_id for item in old_shipment.items}
                for item in new_shipment.items:
                    if (
                        item.item_id not in old_item_ids
                        and self.data_provider.fetch_item_pool().is_item_archived(
                            item.item_id
                        )
                    ):
                        has_archived_entities = old_shipment.items
                        break
        return has_archived_entities

    def is_shipment_archived(self, shipment_id: int) -> bool | None:
        for shipment in self.data:
            if shipment.id == shipment_id:
                return shipment.is_archived
        return None

    def get_shipments_for_order(self, order_id: int) -> List[Shipment]:
        shipments = []
        for shipment in self.data:
            if shipment.order_id == order_id:
                shipments.append(shipment)
        return shipments

    def commit_shipment(self, shipment_id: int) -> Shipment | None:
        if self.is_shipment_archived(shipment_id):
            return None

        for i in range(len(self.data)):
            if self.data[i].id == shipment_id:
                if self.data[i].shipment_status == "Pending":
                    self.data[i].shipment_status = "Transit"
                    self.data_provider.fetch_order_pool().check_if_order_transit(
                        self.data[i].order_id
                    )
                    return self.update_shipment(shipment_id, self.data[i])
                elif self.data[i].shipment_status == "Transit":
                    self.data[i].shipment_status = "Delivered"
                    self.data_provider.fetch_order_pool().check_if_order_delivered(
                        self.data[i].order_id
                    )
                    return self.update_shipment(shipment_id, self.data[i])
        return None
