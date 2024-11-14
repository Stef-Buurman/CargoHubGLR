import json
from typing import List
from models.v2.inventory import Inventory
from models.base import Base
from services.database_service import DatabaseService
from utils.globals import *

INVENTORIES = []


class InventoryService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "inventories.json"
        self.load(is_debug)
        self.db = DatabaseService()

    def get_inventories(self) -> List[Inventory]:
        return self.data

    def get_inventory(self, inventory_id: int) -> Inventory | None:
        for x in self.data:
            if x.id == inventory_id:
                return x
        return None

    def get_inventories_for_item(self, item_id: str) -> List[Inventory]:
        result = []
        for x in self.data:
            if x.item_id == item_id:
                result.append(x)
        return result

    def get_inventory_totals_for_item(self, item_id: str) -> dict:
        result = {
            "total_expected": 0,
            "total_ordered": 0,
            "total_allocated": 0,
            "total_available": 0,
        }
        for x in self.data:
            if x.item_id == item_id:
                result["total_expected"] += x.total_expected
                result["total_ordered"] += x.total_ordered
                result["total_allocated"] += x.total_allocated
                result["total_available"] += x.total_available
        return result

    def add_inventory(self, inventory: Inventory) -> Inventory:
        inventory.created_at = self.get_timestamp()
        inventory.updated_at = self.get_timestamp()
        self.data.append(inventory)
        return inventory

    def update_inventory(self, inventory_id: int, inventory: Inventory) -> Inventory:
        inventory.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == inventory_id:
                self.data[i] = inventory
                break
        return inventory

    def remove_inventory(self, inventory_id: int):
        for x in self.data:
            if x.id == inventory_id:
                self.data.remove(x)

    def load(self, is_debug: bool, inventories: List[Inventory] | None = None):
        if is_debug and inventories is not None:
            self.data = inventories
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Inventory(**inventory_dict) for inventory_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([inventory.model_dump() for inventory in self.data], f)
    
    def insert_inventory(self, inventory: Inventory, closeConnection:bool = True) -> Inventory:
        table_name = inventory.table_name()

        inventory.created_at = self.get_timestamp()
        inventory.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(inventory).items():
            if key != "id" and key != "locations":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)
            inventory_id = cursor.lastrowid

            if inventory.locations:
                for location_id in inventory.locations:
                    location_insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    conn.execute(location_insert_sql, (inventory_id, location_id))

        if closeConnection:
            self.db.commit_and_close()
        return inventory
