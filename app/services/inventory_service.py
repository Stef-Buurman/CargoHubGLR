import json
from typing import List
from models.v2.inventory import Inventory
from models.base import Base
from services.database_service import DB
from utils.globals import *

INVENTORIES = []


class InventoryService(Base):
    def __init__(
        self, is_debug: bool = False, inventories: List[Inventory] | None = None
    ):
        self.db = DB
        self.load(is_debug, inventories)

    def get_inventories(self) -> List[Inventory]:
        all_inventories = []
        with self.db.get_connection() as conn:
            cursor_inventories = conn.execute(f"SELECT * FROM {Inventory.table_name()}")
            rows = cursor_inventories.fetchall()

            cursor_locations = conn.execute(
                f"SELECT inventory_id, location_id FROM {inventory_locations_table}"
            )
            location_rows = cursor_locations.fetchall()

            locations_by_inventory = {}
            for inventory_id, location_id in location_rows:
                if inventory_id not in locations_by_inventory:
                    locations_by_inventory[inventory_id] = []
                locations_by_inventory[inventory_id].append(location_id)

            for inventory in rows:
                inventory_dict = {
                    col[0]: inventory[i]
                    for i, col in enumerate(cursor_inventories.description)
                }
                inventory_dict["locations"] = locations_by_inventory.get(
                    inventory_dict["id"], []
                )
                all_inventories.append(Inventory(**inventory_dict))

        return all_inventories

    def get_inventory(self, inventory_id: int) -> Inventory | None:
        for inventory in self.data:
            if inventory.id == inventory_id:
                return inventory
        return None

    def get_inventories_for_item(self, item_id: str) -> List[Inventory]:
        result = []
        for inventory in self.data:
            if inventory.item_id == item_id:
                result.append(inventory)
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

    def get_key_values_of_inventorie(self, inventory: Inventory) -> dict:
        fields = {}
        for key, value in vars(inventory).items():
            if key != "id" and key != "locations":
                fields[key] = value
        return fields

    def add_inventory(
        self, inventory: Inventory, closeConnection: bool = True
    ) -> Inventory:
        table_name = inventory.table_name()

        inventory.created_at = self.get_timestamp()
        inventory.updated_at = self.get_timestamp()

        fields = self.get_key_values_of_inventorie(inventory)

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection_without_close() as conn:
            cursor_inventory = conn.execute(insert_sql, values)
            inventory.id = cursor_inventory.lastrowid

            if inventory.locations:
                for location_id in inventory.locations:
                    location_insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    conn.execute(location_insert_sql, (inventory.id, location_id))

        if closeConnection:
            self.db.commit_and_close()

        self.data.append(inventory)
        return inventory

    def update_inventory(self, inventory_id: int, inventory: Inventory, closeConnection: bool = True) -> Inventory:
        if(self.get_inventory(inventory_id) is None):
            return None
        table_name = inventory.table_name()

        inventory.updated_at = self.get_timestamp()

        fields = self.get_key_values_of_inventorie(inventory)

        columns = ", ".join(f"{key} = ?" for key in fields.keys())
        values = tuple(fields.values())
        update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"

        with self.db.get_connection_without_close() as conn:
        # Update inventory
            conn.execute(update_sql, values + (inventory_id,))

            if inventory.locations:
                # Fetch existing locations for the inventory
                select_sql = f"SELECT location_id FROM {inventory_locations_table} WHERE inventory_id = ?"
                existing_locations = set()
                for row in conn.execute(select_sql, (inventory_id,)):
                    existing_locations.add(row[0])

                # Determine locations to delete and insert
                new_locations = set(inventory.locations)
                locations_to_delete = set()
                locations_to_insert = set()

                for loc_id in existing_locations:
                    if loc_id not in new_locations:
                        locations_to_delete.add(loc_id)

                for loc_id in new_locations:
                    if loc_id not in existing_locations:
                        locations_to_insert.add(loc_id)

                # Delete obsolete locations
                if locations_to_delete:
                    delete_sql = f"DELETE FROM {inventory_locations_table} WHERE inventory_id = ? AND location_id = ?"
                    delete_values = []
                    for loc_id in locations_to_delete:
                        delete_values.append((inventory_id, loc_id))
                    conn.executemany(delete_sql, delete_values)

                # Insert new locations
                if locations_to_insert:
                    insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    insert_values = []
                    for loc_id in locations_to_insert:
                        insert_values.append((inventory_id, loc_id))
                    conn.executemany(insert_sql, insert_values)

        if closeConnection:
            self.db.commit_and_close()

        for i in range(len(self.data)):
            if self.data[i].id == inventory_id:
                self.data[i] = inventory
                break
        return inventory

    def remove_inventory(self, inventory_id: int):
        for inventory in self.data:
            if inventory.id == inventory_id:
                if self.db.delete(Inventory, inventory_id):
                    self.data.remove(inventory)

    def load(self, is_debug: bool, inventories: List[Inventory] | None = None):
        if is_debug and inventories is not None:
            self.data = inventories
        else:
            self.data = self.get_inventories()
