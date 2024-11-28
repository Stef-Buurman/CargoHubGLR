import json
from typing import List, Optional
from models.v2.shipment import Shipment
from models.v2.ItemInObject import ItemInObject
from models.base import Base
from services.database_service import DB
from services import data_provider_v2
from utils.globals import *

SHIPMENTS = []


class ShipmentService(Base):
    def __init__(self, is_debug: bool = False):
        self.db = DB
        self.load(is_debug)

    def get_shipments(self) -> List[Shipment]:
        shipments = []
        query = """
        SELECT s.*, i.item_uid, i.amount
        FROM shipments s
        LEFT JOIN shipment_items i ON s.id = i.shipment_id
        """
        with self.db.get_connection_without_close() as conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            shipments_dict = {}
            for row in rows:
                row_dict = dict(zip(columns, row))
                shipment_id = row_dict["id"]
                if shipment_id not in shipments_dict:
                    shipments_dict[shipment_id] = Shipment(
                        **{
                            k: v
                            for k, v in row_dict.items()
                            if k not in ["item_uid", "amount"]
                        }
                    )
                    shipments_dict[shipment_id].items = []
                item = ItemInObject(
                    item_id=row_dict["item_uid"], amount=row_dict["amount"]
                )
                shipments_dict[shipment_id].items.append(item)
            shipments = list(shipments_dict.values())
        return shipments

    def get_shipment(self, shipment_id: str) -> Optional[Shipment]:
        for shipment in self.data:
            if shipment.id == shipment_id:
                return shipment

        with self.db.get_connection() as conn:
            query = f"SELECT * FROM {Shipment.table_name()} WHERE id = {shipment_id}"
            cursor = conn.execute(query)
            shipment = cursor.fetchone()
            if shipment:
                query_items = f"SELECT item_uid, amount FROM {shipment_items_table} WHERE shipment_id = {shipment_id}"
                cursor = conn.execute(query_items)
                all_shipment_items = cursor.fetchall()
                shipment["items"] = all_shipment_items
                return Shipment(**shipment)
        return None

    def get_items_in_shipment(self, shipment_id: str) -> Optional[List[ItemInObject]]:
        shipment = self.get_shipment(shipment_id)
        return shipment.items if shipment else None

    def add_shipment(
        self, shipment: Shipment, closeConnection: bool = True
    ) -> Shipment:
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

        with self.db.get_connection_without_close() as conn:
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

        if closeConnection:
            self.db.commit_and_close()
        self.data.append(shipment)
        return shipment

    def update_shipment(
        self, shipment_id: str, shipment: Shipment, closeConnection: bool = True
    ) -> Shipment:
        table_name = shipment.table_name()
        shipment.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(shipment).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(f"{key} = ?" for key in fields)
        values = tuple(fields.values())

        update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"
        with self.db.get_connection_without_close() as conn:
            conn.execute(update_sql, values + (shipment_id,))

            if shipment.items:
                conn.execute(
                    f"DELETE FROM {shipment_items_table} WHERE shipment_id = ?",
                    (shipment_id,),
                )
                for shipment_items in shipment.items:
                    items_insert_sql = f"""
                    INSERT INTO {shipment_items_table} (shipment_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (shipment_id, shipment_items.item_id, shipment_items.amount),
                    )
        if closeConnection:
            self.db.commit_and_close()

        if self.get_shipment(shipment_id) is not None:
            self.data[self.data.index(self.get_shipment(shipment_id))] = shipment

        return shipment

    def update_items_in_shipment(self, shipment_id: str, items: List[dict]):
        shipment = self.get_shipment(shipment_id)
        if shipment:
            self.update_inventory_for_items(shipment.items, items)
            shipment.items = items
            self.update_shipment(shipment_id, shipment)
            return shipment

    def update_inventory_for_items(
        self, current_items: List[Shipment], new_items: List[dict]
    ):
        def update_inventory(item_id, amount_change):
            inventories = (
                data_provider_v2.fetch_inventory_pool().get_inventories_for_item(
                    item_id
                )
            )
            max_inventory = max(
                inventories, key=lambda z: z["total_ordered"], default=None
            )
            if max_inventory:
                max_inventory["total_ordered"] += amount_change
                max_inventory["total_expected"] = (
                    max_inventory["total_on_hand"] + max_inventory["total_ordered"]
                )
                data_provider_v2.fetch_inventory_pool().update_inventory(
                    max_inventory["id"], max_inventory
                )

        new_items_dict = {item["item_id"]: item for item in new_items}
        for current in current_items:
            item_id = current.item_id
            current_amount = current.amount
            if item_id in new_items_dict:
                new_amount = new_items_dict[item_id]["amount"]
                amount_change = new_amount - current_amount
                update_inventory(item_id, amount_change)
            else:
                update_inventory(item_id, -current_amount)
        current_item_ids = {current.item_id for current in current_items}
        for item in new_items:
            if item["item_id"] not in current_item_ids:
                update_inventory(item["item_id"], item["amount"])

    def remove_shipment(self, shipment_id: str, closeConnection: bool = True) -> bool:
        for x in self.data:
            if x.id == shipment_id:
                if self.db.delete(Shipment, shipment_id, closeConnection):
                    self.data.remove(x)
                    return True
        return False

    def load(self, is_debug: bool, shipments: List[Shipment] | None = None):
        if is_debug and shipments is not None:
            self.data = shipments
        else:
            self.data = self.get_shipments()
