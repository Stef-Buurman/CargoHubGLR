import json
from typing import List, Optional
from models.v2.shipment import Shipment
from models.base import Base
from app.services import data_provider

SHIPMENTS = []


class ShipmentService(Base):
    def __init__(self, root_path: str, is_debug: bool = False):
        self.data_path = root_path + "shipments.json"
        self.load(is_debug)
        self.current_id = 0

    def get_shipments(self) -> List[Shipment]:
        return self.data

    def get_shipment(self, shipment_id: str) -> Optional[Shipment]:
        return next((shipment for shipment in self.data if shipment.id == shipment_id), None)

    def get_items_in_shipment(self, shipment_id: str) -> Optional[List[dict]]:
        shipment = self.get_shipment(shipment_id)
        return shipment.items if shipment else None

    def add_shipment(self, shipment: Shipment) -> Shipment:
        shipment.id = self.generate_uid()
        shipment.created_at = self.get_timestamp()
        shipment.updated_at = self.get_timestamp()
        self.data.append(shipment)
        return shipment

    def generate_uid(self) -> str:
        self.current_id = max((int(shipment.id[1:]) for shipment in self.data), default=0)
        new_uid = f"S{self.current_id + 1:06d}"
        return new_uid

    def update_shipment(self, shipment_id: str, shipment: Shipment):
        shipment.updated_at = self.get_timestamp()
        for i, existing_shipment in enumerate(self.data):
            if existing_shipment.id == shipment_id:
                self.data[i] = shipment
                return shipment

    def update_items_in_shipment(self, shipment_id: str, items: List[dict]):
        shipment = self.get_shipment(shipment_id)
        if shipment:
            self.update_inventory_for_items(shipment.items, items)
            shipment.items = items
            self.update_shipment(shipment_id, shipment)

    def update_inventory_for_items(self, current_items: List[dict], new_items: List[dict]):
        def update_inventory(item_id, amount_change):
            inventories = data_provider.fetch_inventory_pool().get_inventories_for_item(item_id)
            max_inventory = max(inventories, key=lambda z: z["total_ordered"], default=None)
            if max_inventory:
                max_inventory["total_ordered"] += amount_change
                max_inventory["total_expected"] = max_inventory["total_on_hand"] + max_inventory["total_ordered"]
                data_provider.fetch_inventory_pool().update_inventory(max_inventory["id"], max_inventory)

        for current in current_items:
            if not any(current["item_id"] == item["item_id"] for item in new_items):
                update_inventory(current["item_id"], -current["amount"])

        for current in current_items:
            for new in new_items:
                if current["item_id"] == new["item_id"]:
                    amount_change = new["amount"] - current["amount"]
                    update_inventory(current["item_id"], amount_change)

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
