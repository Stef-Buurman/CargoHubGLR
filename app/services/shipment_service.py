import json
from typing import List, Optional
from models.v2.shipment import Shipment
from models.base import Base
from services.data_provider_v2 import fetch_inventory_pool
from services.database_service import DatabaseService
from utils.globals import *

SHIPMENTS = []


class ShipmentService(Base):
    def __init__(self, root_path: str, is_debug: bool = False):
        self.data_path = root_path + "shipments.json"
        self.load(is_debug)
        self.current_id = 0
        self.db = DatabaseService()

    def get_shipments(self) -> List[Shipment]:
        return self.data

    def get_shipment(self, shipment_id: str) -> Optional[Shipment]:
        return next((shipment for shipment in self.data if shipment.id == shipment_id), None)

    def get_items_in_shipment(self, shipment_id: str) -> Optional[List[dict]]:
        shipment = self.get_shipment(shipment_id)
        return shipment.items if shipment else None

    def add_shipment(self, shipment: Shipment) -> Shipment:
        shipment.created_at = self.get_timestamp()
        shipment.updated_at = self.get_timestamp()
        self.data.append(shipment)
        return shipment

    def update_shipment(self, shipment_id: str, shipment: Shipment):
        shipment.updated_at = self.get_timestamp()
        for i, existing_shipment in enumerate(self.data):
            if existing_shipment.id == shipment_id:
                self.data[i] = shipment
                break
        return shipment

    def update_items_in_shipment(self, shipment_id: str, items: List[dict]):
        shipment = self.get_shipment(shipment_id)
        if shipment:
            self.update_inventory_for_items(shipment.items, items)
            shipment.items = items
            self.update_shipment(shipment_id, shipment)
            return shipment

    def update_inventory_for_items(self, current_items: List[Shipment], new_items: List[dict]):
        def update_inventory(item_id, amount_change):
            inventories = fetch_inventory_pool().get_inventories_for_item(item_id)
            max_inventory = max(inventories, key=lambda z: z["total_ordered"], default=None)
            if max_inventory:
                max_inventory["total_ordered"] += amount_change
                max_inventory["total_expected"] = max_inventory["total_on_hand"] + max_inventory["total_ordered"]
                fetch_inventory_pool().update_inventory(max_inventory["id"], max_inventory)
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

    def remove_shipment(self, shipment_id: str):
        shipment = self.get_shipment(shipment_id)
        if shipment:
            self.data.remove(shipment)

    def load(self, is_debug: bool):
        if is_debug:
            self.data = SHIPMENTS
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Shipment(**shipment_dict) for shipment_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([shipment.model_dump() for shipment in self.data], f)

    def insert_shipment(self, shipment: Shipment, closeConnection:bool = True) -> Shipment:
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
                    conn.execute(items_insert_sql, (shipment_id, shipment_items.item_id, shipment_items.amount))
        
        if closeConnection:
            self.db.commit_and_close()
        return shipment
