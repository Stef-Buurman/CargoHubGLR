import json
from models.v2.order import Order
from .base import Base
from services.v2 import data_provider_v2
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from services.v1 import data_provider

ORDERS = []


class Orders(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "orders.json"
        self.load(is_debug)

    def get_orders(self):
        return self.data

    def get_order(self, order_id):
        for x in self.data:
            if x["id"] == order_id:
                return x
        return None

    def get_items_in_order(self, order_id):
        for x in self.data:
            if x["id"] == order_id:
                return x["items"]
        return None

    def get_orders_in_shipment(self, shipment_id):
        result = []
        for x in self.data:
            if x["shipment_id"] == shipment_id:
                result.append(x["id"])
        return result

    def get_orders_for_shipments(self, shipment_id):
        result = []
        for x in self.data:
            if x["shipment_id"] == shipment_id:
                result.append(x)
        return result

    def get_orders_for_client(self, client_id):
        result = []
        for x in self.data:
            if x["ship_to"] == client_id or x["bill_to"] == client_id:
                result.append(x)
        return result

    def add_order(self, order):
        if self.is_debug:
            order["created_at"] = self.get_timestamp()
            order["updated_at"] = self.get_timestamp()
            self.data.append(order)
            return order
        else:
            added_order = data_provider_v2.fetch_order_pool().add_order(
                Order(**order), False
            )
            return added_order.model_dump()

    def update_order(self, order_id, order):
        order["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == order_id:
                order["id"] = order_id
                if order.get("created_at") is None:
                    order["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = order
                    return order
                else:
                    updated_order = data_provider_v2.fetch_order_pool().update_order(
                        order_id, Order(**order), False
                    )
                    return updated_order.model_dump()

    def update_items_in_order(self, order_id, items):
        order = self.get_order(order_id)
        current = order["items"]
        for current_item in current:
            found = False
            for updated_item in items:
                if current_item["item_id"] == updated_item["item_id"]:
                    found = True
                    break
            if not found:
                inventories = (
                    data_provider.fetch_inventory_pool().get_inventories_for_item(
                        current_item["item_id"]
                    )
                )
                min_ordered = float("inf")
                min_inventory = None

                for inv in inventories:
                    if inv["total_allocated"] > min_ordered:
                        min_ordered = inv["total_allocated"]
                        min_inventory = inv

                if min_inventory:
                    min_inventory["total_allocated"] -= current_item["amount"]
                    min_inventory["total_expected"] = (
                        min_inventory["total_on_hand"] + min_inventory["total_ordered"]
                    )
                    data_provider.fetch_inventory_pool().update_inventory(
                        min_inventory["id"], min_inventory
                    )

        for updated_item in items:
            found = False
            matching_current_item = None

            for current_item in current:
                if current_item["item_id"] == updated_item["item_id"]:
                    found = True
                    matching_current_item = current_item
                    break

            if found:
                inventories = (
                    data_provider.fetch_inventory_pool().get_inventories_for_item(
                        updated_item["item_id"]
                    )
                )
                min_inventory = None
                min_ordered = float("inf")

                for inv in inventories:
                    if inv["total_allocated"] < min_ordered:
                        min_ordered = inv["total_allocated"]
                        min_inventory = inv

                if min_inventory:
                    delta_amount = (
                        updated_item["amount"] - matching_current_item["amount"]
                    )
                    min_inventory["total_allocated"] += delta_amount
                    min_inventory["total_expected"] = (
                        min_inventory["total_on_hand"] + min_inventory["total_ordered"]
                    )
                    data_provider.fetch_inventory_pool().update_inventory(
                        min_inventory["id"], min_inventory
                    )

        order["items"] = items
        return self.update_order(order_id, order)

    def update_orders_in_shipment(self, shipment_id, orders):
        packed_orders = self.get_orders_in_shipment(shipment_id)
        for x in packed_orders:
            if x not in orders:
                order = self.get_order(x)
                order["shipment_id"] = -1
                order["order_status"] = "Scheduled"
                self.update_order(x, order)
        for x in orders:
            order = self.get_order(x)
            order["shipment_id"] = shipment_id
            order["order_status"] = "Packed"
            return self.update_order(x, order)

    def remove_order(self, order_id):
        for x in self.data:
            if x["id"] == order_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_order_pool().archive_order(order_id, False)

    def load(self, is_debug):
        if is_debug:
            self.data = ORDERS
        else:
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):
        if data is not None:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
