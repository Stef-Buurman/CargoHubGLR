import json
from models.v2.inventory import Inventory

from .base import Base
from services.v2 import data_provider_v2

INVENTORIES = []


class Inventories(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "inventories.json"
        self.is_debug = is_debug
        self.load(is_debug)

    def get_inventories(self):
        return self.data

    def get_inventory(self, inventory_id):
        for x in self.data:
            if x["id"] == inventory_id:
                return x
        return None

    def get_inventories_for_item(self, item_id):
        result = []
        for x in self.data:
            if x["item_id"] == item_id:
                result.append(x)

        return result

    def get_inventory_totals_for_item(self, item_id):
        result = {
            "total_expected": 0,
            "total_ordered": 0,
            "total_allocated": 0,
            "total_available": 0,
        }
        for x in self.data:
            if x["item_id"] == item_id:
                result["total_expected"] += x["total_expected"]
                result["total_ordered"] += x["total_ordered"]
                result["total_allocated"] += x["total_allocated"]
                result["total_available"] += x["total_available"]
        return result

    def add_inventory(self, inventory):
        if self.is_debug:
            inventory["created_at"] = self.get_timestamp()
            inventory["updated_at"] = self.get_timestamp()
            self.data.append(inventory)
            return inventory
        else:  # pragma: no cover
            created_inventory = data_provider_v2.fetch_inventory_pool().add_inventory(
                Inventory(**inventory), False
            )
            return created_inventory.model_dump()

    def update_inventory(self, inventory_id, inventory):
        inventory["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == inventory_id:
                inventory["id"] = inventory_id
                if inventory.get("created_at") is None:
                    inventory["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = inventory
                    return inventory
                else:  # pragma: no cover
                    updated_inventory = (
                        data_provider_v2.fetch_inventory_pool().update_inventory(
                            inventory_id, Inventory(**inventory), False
                        )
                    )
                    return updated_inventory.model_dump()

    def remove_inventory(self, inventory_id):
        for x in self.data:
            if x["id"] == inventory_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_inventory_pool().archive_inventory(
                        inventory_id, False
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = INVENTORIES
        else:  # pragma: no cover
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):  # pragma: no cover
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
