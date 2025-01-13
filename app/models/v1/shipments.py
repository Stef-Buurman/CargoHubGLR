import json
from models.v2.shipment import Shipment

from .base import Base
from services.v2 import data_provider_v2
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from services.v1 import data_provider


class Shipments(Base):
    def __init__(self, root_path, is_debug=False, shipments=None):
        self.is_debug = is_debug
        self.data_path = root_path + "shipments.json"
        self.load(is_debug, shipments)

    def get_shipments(self):
        return self.data

    def get_shipment(self, shipment_id):
        for x in self.data:
            if x["id"] == shipment_id:
                return x
        return None

    def get_items_in_shipment(self, shipment_id):
        for x in self.data:
            if x["id"] == shipment_id:
                return x["items"]
        return None

    def add_shipment(self, shipment):
        if self.is_debug:
            shipment["created_at"] = self.get_timestamp()
            shipment["updated_at"] = self.get_timestamp()
            self.data.append(shipment)
            return shipment
        else:
            created_shipment = data_provider_v2.fetch_shipment_pool().add_shipment(
                Shipment(**shipment)
            )
            return created_shipment.model_dump()

    def update_shipment(self, shipment_id, shipment):
        shipment["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == shipment_id:
                shipment["id"] = shipment_id
                if shipment.get("created_at") is None:
                    shipment["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = shipment
                    return shipment
                else:
                    updated_shipment = (
                        data_provider_v2.fetch_shipment_pool().update_shipment(
                            shipment_id, Shipment(**shipment)
                        )
                    )
                    return updated_shipment.model_dump()

    def update_items_in_shipment(self, shipment_id, items):
        shipment = self.get_shipment(shipment_id)
        current = shipment["items"]
        for x in current:
            found = False
            for y in items:
                if x["item_id"] == y["item_id"]:
                    found = True
                    break
            if not found:
                inventories = (
                    data_provider.fetch_inventory_pool().get_inventories_for_item(
                        x["item_id"]
                    )
                )
                max_ordered = -1
                max_inventory = {}
                for z in inventories:
                    if z["total_ordered"] > max_ordered:
                        max_ordered = z["total_ordered"]
                        max_inventory = z
                if max_inventory:
                    max_inventory["total_ordered"] -= x["amount"]
                    max_inventory["total_expected"] = (
                        y["total_on_hand"] + y["total_ordered"]
                    )
                    data_provider.fetch_inventory_pool().update_inventory(
                        max_inventory["id"], max_inventory
                    )
        for x in current:
            for y in items:
                if x["item_id"] == y["item_id"]:
                    inventories = (
                        data_provider.fetch_inventory_pool().get_inventories_for_item(
                            x["item_id"]
                        )
                    )
                    max_ordered = -1
                    max_inventory = {}
                    for z in inventories:
                        if z["total_ordered"] > max_ordered:
                            max_ordered = z["total_ordered"]
                            max_inventory = z
                    if max_inventory:
                        max_inventory["total_ordered"] += y["amount"] - x["amount"]
                        max_inventory["total_expected"] = (
                            y["total_on_hand"] + y["total_ordered"]
                        )
                        data_provider.fetch_inventory_pool().update_inventory(
                            max_inventory["id"], max_inventory
                        )
        shipment["items"] = items
        self.update_shipment(shipment_id, shipment)

    def remove_shipment(self, shipment_id):
        for x in self.data:
            if x["id"] == shipment_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_shipment_pool().archive_shipment(shipment_id)

    def update_items_for_shipment(self, shipment_id, items):
        shipment = self.get_shipment(shipment_id)
        current_items = shipment["items"]

        def update_inventory(item_id, amount_change):
            inventories = data_provider.fetch_inventory_pool().get_inventories_for_item(
                item_id
            )
            max_inventory = max(
                inventories, key=lambda z: z["total_ordered"], default=None
            )

            if max_inventory:
                max_inventory["total_ordered"] += amount_change
                max_inventory["total_expected"] = (
                    max_inventory["total_on_hand"] + max_inventory["total_ordered"]
                )
                data_provider.fetch_inventory_pool().update_inventory(
                    max_inventory["id"], max_inventory
                )

        for current in current_items:
            if not any(current["item_id"] == item["item_id"] for item in items):
                update_inventory(current["item_id"], -current["amount"])

        for current in current_items:
            for new in items:
                if current["item_id"] == new["item_id"]:
                    amount_change = new["amount"] - current["amount"]
                    update_inventory(current["item_id"], amount_change)

        shipment["items"] = items
        self.update_shipment(shipment_id, shipment)

    def load(self, is_debug, shipments=None):
        if is_debug:
            self.data = shipments
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
