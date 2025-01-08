from typing import List, Type
from models.v2.inventory import Inventory
from services.v2.base_service import Base
from services.v2.database_service import DB, DatabaseService
from services.v2 import data_provider_v2
from services.v1 import data_provider
from utils.globals import *


class InventoryService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = DB
        self.load()

    def get_all_inventories(self) -> List[Inventory]:
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

    def get_inventories(self) -> List[Inventory]:
        inventories = []
        for inventory in self.data:
            if not inventory.is_archived:
                inventories.append(inventory)
        return inventories

    def get_inventory(self, inventory_id: int) -> Inventory | None:
        for inventory in self.data:
            if inventory.id == inventory_id:
                return inventory

        with self.db.get_connection() as conn:
            cursor_inventories = conn.execute(
                f"SELECT * FROM {Inventory.table_name()} WHERE id = {inventory_id}"
            )
            inventory = cursor_inventories.fetchone()

            cursor_locations = conn.execute(
                f"SELECT inventory_id, location_id FROM {inventory_locations_table} WHERE inventory_id = {inventory_id}"
            )
            location_rows = cursor_locations.fetchall()

            if inventory:
                inventory["locations"] = []
                for inventory_id, location_id in location_rows:
                    inventory["locations"].append(location_id)

                return Inventory(**inventory)

        return None

    def add_inventory(self, inventory: Inventory) -> Inventory | None:
        if self.has_inventory_archived_entities(inventory):
            return None

        table_name = inventory.table_name()

        inventory.created_at = self.get_timestamp()
        inventory.updated_at = self.get_timestamp()

        fields = self.get_key_values_of_inventory(inventory)

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection() as conn:
            cursor_inventory = conn.execute(insert_sql, values)
            inventory.id = cursor_inventory.lastrowid

            if inventory.locations:
                for location_id in inventory.locations:
                    location_insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    conn.execute(location_insert_sql, (inventory.id, location_id))
        self.data.append(inventory)
        self.save()
        return inventory

    def update_inventory(self, inventory_id: int, inventory: Inventory) -> Inventory:
        if (
            self.get_inventory(inventory_id) is None
            or self.is_inventory_archived(inventory_id)
            or self.has_inventory_archived_entities(
                inventory, self.get_inventory(inventory_id)
            )
        ):
            return None
        table_name = inventory.table_name()

        inventory.updated_at = self.get_timestamp()

        fields = self.get_key_values_of_inventory(inventory)

        columns = ", ".join(f"{key} = ?" for key in fields.keys())
        values = tuple(fields.values())
        update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"

        with self.db.get_connection() as conn:
            conn.execute(update_sql, values + (inventory_id,))

            if inventory.locations:
                select_sql = f"SELECT location_id FROM {inventory_locations_table} WHERE inventory_id = ?"
                existing_locations = set()
                for row in conn.execute(select_sql, (inventory_id,)):
                    existing_locations.add(row[0])

                new_locations = set(inventory.locations)
                locations_to_delete = set()
                locations_to_insert = set()

                for loc_id in existing_locations:
                    if loc_id not in new_locations:
                        locations_to_delete.add(loc_id)

                for loc_id in new_locations:
                    if loc_id not in existing_locations:
                        locations_to_insert.add(loc_id)

                if locations_to_delete:
                    delete_sql = f"DELETE FROM {inventory_locations_table} WHERE inventory_id = ? AND location_id = ?"
                    delete_values = []
                    for loc_id in locations_to_delete:
                        delete_values.append((inventory_id, loc_id))
                    conn.executemany(delete_sql, delete_values)

                if locations_to_insert:
                    insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    insert_values = []
                    for loc_id in locations_to_insert:
                        insert_values.append((inventory_id, loc_id))
                    conn.executemany(insert_sql, insert_values)
        for i in range(len(self.data)):
            if self.data[i].id == inventory_id:
                self.data[i] = inventory
                self.save()
                break
        return inventory

    def archive_inventory(self, inventory_id: int) -> Inventory | None:
        for i in range(len(self.data)):
            if self.data[i].id == inventory_id:
                self.data[i].is_archived = True
                table_name = self.data[i].table_name()

                self.data[i].updated_at = self.get_timestamp()

                fields = self.get_key_values_of_inventory(self.data[i])

                columns = ", ".join(f"{key} = ?" for key in fields.keys())
                values = tuple(fields.values())
                update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values + (inventory_id,))
                self.save()
                return self.data[i]
        return None

    def unarchive_inventory(self, inventory_id: int) -> Inventory | None:
        for i in range(len(self.data)):
            if self.data[i].id == inventory_id:
                self.data[i].is_archived = False
                table_name = self.data[i].table_name()

                self.data[i].updated_at = self.get_timestamp()

                fields = self.get_key_values_of_inventory(self.data[i])

                columns = ", ".join(f"{key} = ?" for key in fields.keys())
                values = tuple(fields.values())
                update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values + (inventory_id,))
                self.save()
                return self.data[i]
        return False

    def save(self):
        if not self.is_debug:
            data_provider.fetch_inventory_pool().save(
                [inventory.model_dump() for inventory in self.data]
            )

    def load(self):
        self.data = self.get_all_inventories()

    def is_inventory_archived(self, inventory_id: int) -> bool | None:
        inventory = self.get_inventory(inventory_id)
        if inventory:
            return inventory.is_archived
        return None

    def has_inventory_archived_entities(
        self, new_inventory: Inventory, old_inventory: Inventory | None = None
    ) -> bool:
        has_archived_entities = False
        if old_inventory is None:
            has_archived_entities = data_provider_v2.fetch_item_pool().is_item_archived(
                new_inventory.item_id
            )
            for location_id in new_inventory.locations:
                is_location_archived = (
                    data_provider_v2.fetch_location_pool().is_location_archived(
                        location_id
                    )
                )
                if is_location_archived:
                    has_archived_entities = True
                    break
        else:
            if new_inventory.item_id != old_inventory.item_id:
                has_archived_entities = (
                    data_provider_v2.fetch_item_pool().is_item_archived(
                        new_inventory.item_id
                    )
                )
            for location_id in new_inventory.locations:
                if location_id not in old_inventory.locations:
                    is_location_archived = (
                        data_provider_v2.fetch_location_pool().is_location_archived(
                            location_id
                        )
                    )
                    if is_location_archived:
                        has_archived_entities = True
                        break
        return has_archived_entities

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

    def get_key_values_of_inventory(self, inventory: Inventory) -> dict:
        fields = {}
        for key, value in vars(inventory).items():
            if key != "id" and key != "locations":
                fields[key] = value
        return fields
