from typing import List, Type
from services.v2 import data_provider_v2
from models.v2.order import Order
from services.v2.base_service import Base
from models.v2.ItemInObject import ItemInObject
from utils.globals import *
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class OrderService(Base):
    def __init__(
        self,
        db: Type[DatabaseService] = None,
        data_provider=None,
        is_debug: bool = False,
    ):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()

        if data_provider is not None:
            self.data_provider = data_provider
        else:
            self.data_provider = data_provider_v2
        self.load()

    def get_all_orders(self) -> List[Order]:
        all_orders = self.db.get_all(Order)
        order_ids = [order.id for order in all_orders]

        with self.db.get_connection() as conn:
            query = f"SELECT item_id, amount, order_id FROM {order_items_table} WHERE order_id IN ({', '.join(map(str, order_ids))})"
            cursor = conn.execute(query)
            all_order_items = cursor.fetchall()

        order_items_map = {}
        for row in all_order_items:
            if row[2] not in order_items_map:
                order_items_map[row[2]] = []
            order_items_map[row[2]].append(ItemInObject(item_id=row[0], amount=row[1]))

        for order in all_orders:
            order.items = order_items_map.get(order.id, [])

        return all_orders

    def get_orders(self) -> List[Order]:
        orders = []
        for order in self.data:
            if not order.is_archived:
                orders.append(order)
        return orders

    def get_order(self, order_id: int) -> Order | None:
        for order in self.data:
            if order.id == order_id:
                return order

        with self.db.get_connection() as conn:
            query = f"SELECT * FROM {Order.table_name()} WHERE id = ?"
            cursor = conn.execute(query, (order_id,))
            order_row = cursor.fetchone()
            if order_row:
                column_names = [description[0] for description in cursor.description]
                order = dict(zip(column_names, order_row))
                query_items = f"SELECT item_id, amount, order_id FROM {order_items_table} WHERE order_id = {order_id}"
                cursor = conn.execute(query_items)
                all_order_items = cursor.fetchall()
                order["items"] = [
                    ItemInObject(item_id=row[0], amount=row[1])
                    for row in all_order_items
                ]
                return Order(**order)
        return None

    def get_items_in_order(self, order_id: int) -> List[ItemInObject]:
        for order in self.data:
            if order.id == order_id:
                return order.items
        return None

    def get_orders_in_shipment(self, shipment_id: int) -> List[Order]:
        result = []
        for order in self.data:
            if order.shipment_id == shipment_id:
                result.append(order)
        return result

    def get_orders_for_client(self, client_id: str) -> List[Order]:
        result = []
        for order in self.data:
            if order.ship_to == client_id or order.bill_to == client_id:
                result.append(order)
        return result

    def add_order(self, order: Order, background_task=True) -> Order:
        if self.has_order_archived_entities(order):
            return None

        table_name = order.table_name()

        order.created_at = self.get_timestamp()
        order.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(order).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"""INSERT INTO {
            table_name} ({columns}) VALUES ({placeholders})"""

        with self.db.get_connection() as conn:
            cursor = conn.execute(insert_sql, values)
            order_id = cursor.lastrowid
            order.id = order_id

            if order.items:
                for order_items in order.items:
                    items_insert_sql = f"""
                    INSERT INTO {order_items_table} (order_id, item_id, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (order_id, order_items.item_id, order_items.amount),
                    )
        self.data.append(order)
        self.save(background_task)
        return order

    def update_order(
        self, order_id: int, order: Order, background_task=True
    ) -> Order | None:
        if self.is_order_archived(
            order_id
        ) is not False or self.has_order_archived_entities(
            order, self.get_order(order_id)
        ):
            return None

        table_name = order.table_name()
        order.id = order_id
        if order.created_at is None:
            existing_order = self.get_order(order_id)
            order.created_at = existing_order.created_at
        order.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(order).items():
            if key != "items":
                fields[key] = value

        set_clause = ", ".join(f"{key} = ?" for key in fields if key != "id")
        values = tuple(fields[key] for key in fields if key != "id") + (order_id,)

        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

        with self.db.get_connection() as conn:
            conn.execute(update_sql, values)
            existing_order = self.get_order(order_id)
            if existing_order and existing_order.items != order.items:
                delete_items_sql = f"""DELETE FROM {
                    order_items_table} WHERE order_id = ?"""
                conn.execute(delete_items_sql, (order_id,))

                if order.items:
                    for order_items in order.items:
                        items_insert_sql = f"""
                        INSERT INTO {order_items_table} (order_id, item_id, amount)
                        VALUES (?, ?, ?)
                        """
                        conn.execute(
                            items_insert_sql,
                            (order_id, order_items.item_id, order_items.amount),
                        )

        for i in range(len(self.data)):
            if self.data[i].id == order_id:
                self.data[i] = order
        self.save(background_task)
        return order

    def update_items_in_order(
        self, order_id: int, items: List[ItemInObject]
    ) -> Order | None:
        order = self.get_order(order_id)
        if order.is_archived:
            return None

        order.items = []
        for item in items:
            if not self.data_provider.fetch_item_pool().is_item_archived(item.item_id):
                order.items.append(item)
        return self.update_order(order_id, order)

    def update_orders_in_shipment(
        self, shipment_id: int, orders: List[Order]
    ) -> List[Order]:
        updated_orders = []
        packed_orders = self.get_orders_in_shipment(shipment_id)
        for packed_order in packed_orders:
            if packed_order not in orders:
                if not packed_order.is_archived:
                    packed_order.shipment_id = -1
                    packed_order.order_status = "Scheduled"
                    self.update_order(packed_order.id, packed_order)

        for order in orders:
            if not order.is_archived:
                order.shipment_id = shipment_id
                order.order_status = "Packed"
                updated_orders.append(self.update_order(order.id, order))
        return updated_orders

    def archive_order(self, order_id: int, background_task=True) -> Order | None:
        for i in range(len(self.data)):
            if self.data[i].id == order_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = (
                    f"UPDATE {self.data[i].table_name()} SET {columns} WHERE id = ?"
                )
                values += (order_id,)

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values)
                self.save(background_task)
                return self.data[i]
        return None

    def unarchive_order(self, order_id: int, background_task=True) -> Order | None:
        for i in range(len(self.data)):
            if self.data[i].id == order_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = (
                    f"UPDATE {self.data[i].table_name()} SET {columns} WHERE id = ?"
                )
                values += (order_id,)

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values)
                self.save(background_task)
                return self.data[i]
        return None

    def save(self, background_task=True):
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_order_pool().save(
                    [order.model_dump() for order in self.data]
                )

            if background_task:
                self.data_provider.fetch_background_tasks().add_task(
                    call_v1_save_method
                )
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_orders()

    def is_order_archived(self, order_id: int) -> bool:
        for order in self.data:
            if order.id == order_id:
                return order.is_archived
        return None

    def has_order_archived_entities(
        self, new_order: Order, old_order: Order | None = None
    ) -> bool:
        has_archived_entities = False

        if old_order is None:
            if new_order.ship_to is not None:
                has_archived_entities = (
                    self.data_provider.fetch_client_pool().is_client_archived(
                        new_order.ship_to
                    )
                )
            if not has_archived_entities and new_order.bill_to is not None:
                has_archived_entities = (
                    self.data_provider.fetch_client_pool().is_client_archived(
                        new_order.bill_to
                    )
                )
            if not has_archived_entities and new_order.shipment_id is not None:
                has_archived_entities = (
                    self.data_provider.fetch_shipment_pool().is_shipment_archived(
                        new_order.shipment_id
                    )
                )
            if not has_archived_entities and new_order.warehouse_id is not None:
                has_archived_entities = (
                    self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                        new_order.warehouse_id
                    )
                )
        else:
            if new_order.ship_to != old_order.ship_to and new_order.ship_to is not None:
                has_archived_entities = (
                    self.data_provider.fetch_client_pool().is_client_archived(
                        new_order.ship_to
                    )
                )
            if (
                not has_archived_entities
                and new_order.bill_to != old_order.bill_to
                and new_order.bill_to is not None
            ):
                has_archived_entities = (
                    self.data_provider.fetch_client_pool().is_client_archived(
                        new_order.bill_to
                    )
                )
            if (
                not has_archived_entities
                and new_order.shipment_id != old_order.shipment_id
                and new_order.shipment_id is not None
            ):
                has_archived_entities = (
                    self.data_provider.fetch_shipment_pool().is_shipment_archived(
                        new_order.shipment_id
                    )
                )
            if (
                not has_archived_entities
                and new_order.warehouse_id != old_order.warehouse_id
                and new_order.warehouse_id is not None
            ):
                has_archived_entities = (
                    self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                        new_order.warehouse_id
                    )
                )

        return has_archived_entities

    def check_if_order_transit(self, order_id: int) -> Order | None:
        order = self.get_order(order_id)
        shipments = self.data_provider.fetch_shipment_pool().get_shipments_for_order(
            order_id
        )
        can_change_to_Transit = True
        for shipment in shipments:
            if shipment.shipment_status != "Transit":
                can_change_to_Transit = False
                break
        if can_change_to_Transit:
            order.order_status = "Shipped"
            return self.update_order(order_id, order)
        return None

    def check_if_order_delivered(self, order_id: int) -> Order | None:
        order = self.get_order(order_id)
        shipments = self.data_provider.fetch_shipment_pool().get_shipments_for_order(
            order_id
        )
        can_change_to_delivered = True
        for shipment in shipments:
            if shipment.shipment_status != "Delivered":
                can_change_to_delivered = False
                break
        if can_change_to_delivered:
            order.order_status = "Delivered"
            return self.update_order(order_id, order)
        return None
