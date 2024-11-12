import json
from typing import List
from models.v2.order import Order
from models.base import Base
from services.data_provider_v2 import fetch_inventory_pool
from models.v2.ItemInObject import ItemInObject
from utils.globals import *
from services.database_service import DatabaseService

ORDERS = []


class OrderService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "orders.json"
        self.load(is_debug)
        self.db = DatabaseService()

    def get_orders(self) -> List[Order]:
        return self.data

    def get_order(self, order_id: int) -> Order | None:
        for x in self.data:
            if x.id == order_id:
                return x
        return None

    def get_items_in_order(self, order_id: int) -> List[ItemInObject]:
        for x in self.data:
            if x.id == order_id:
                return x.items
        return None

    def get_orders_in_shipment(self, shipment_id: int) -> List[Order]:
        result = []
        for x in self.data:
            if x.shipment_id == shipment_id:
                result.append(x.id)
        return result

    def get_orders_for_shipments(self, shipment_id: int) -> List[Order]:
        result = []
        for x in self.data:
            if x.shipment_id == shipment_id:
                result.append(x)
        return result

    def get_orders_for_client(self, client_id: str) -> List[Order]:
        result = []
        for x in self.data:
            if x.ship_to == client_id or x.bill_to == client_id:
                result.append(x)
        return result

    def add_order(self, order: Order) -> Order:
        order.created_at = self.get_timestamp()
        order.updated_at = self.get_timestamp()
        self.data.append(order)
        return order

    def update_order(self, order_id: int, order: Order) -> Order | None:
        order.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == order_id:
                self.data[i] = order
                break
        return order

    def update_items_in_order(self, order_id: int, items: List[ItemInObject]) -> Order | None:
        order = self.get_order(order_id)
        current = order.items
        for current_item in current:
            found = False
            for updated_item in items:
                if current_item.item_id == updated_item.item_id:
                    found = True
                    break
            if not found:
                inventories = fetch_inventory_pool().get_inventories_for_item(current_item.item_id)
                min_ordered = float("inf")
                min_inventory = None

                for inv in inventories:
                    if inv.total_allocated > min_ordered:
                        min_ordered = inv.total_allocated
                        min_inventory = inv

                if min_inventory:
                    min_inventory.total_allocated -= current_item.amount
                    min_inventory.total_expected = min_inventory.total_on_hand + min_inventory.total_ordered
                    fetch_inventory_pool().update_inventory(min_inventory.id, min_inventory)

        for updated_item in items:
            found = False
            matching_current_item = None
            
            for current_item in current:
                if current_item.item_id == updated_item.item_id:
                    found = True
                    matching_current_item = current_item
                    break

            if found:
                inventories = fetch_inventory_pool().get_inventories_for_item(updated_item.item_id)
                min_inventory = None
                min_ordered = float("inf")
                
                for inv in inventories:
                    if inv.total_allocated > min_ordered:
                        min_ordered = inv.total_allocated
                        min_inventory = inv

                if min_inventory:
                    delta_amount = updated_item.amount - matching_current_item.amount
                    min_inventory.total_allocated += delta_amount
                    min_inventory.total_expected = min_inventory.total_on_hand + min_inventory.total_ordered
                    fetch_inventory_pool().update_inventory(min_inventory.id, min_inventory)

        order.items = items
        self.update_order(order_id, order)
        return order

    def update_orders_in_shipment(self, shipment_id: int, orders: List[Order]) -> List[Order]:
        packed_orders = self.get_orders_in_shipment(shipment_id)
        for x in packed_orders:
            if x not in orders:
                order = self.get_order(x)
                order.shipment_id = -1
                order.order_status = "Scheduled"
                self.update_order(x, order)
        for x in orders:
            order = self.get_order(x)
            order.shipment_id = shipment_id
            order.order_status = "Packed"
            self.update_order(x, order)
            return order

    def remove_order(self, order_id: int):
        for x in self.data:
            if x.id == order_id:
                self.data.remove(x)

    def load(self, is_debug):
        if is_debug:
            self.data = ORDERS
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Order(**order_dict) for order_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([shipment.model_dump() for shipment in self.data], f)
    
    def insert_order(self, order: Order) -> Order:
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

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection() as conn:
            cursor = conn.execute(insert_sql, values)
            order_id = cursor.lastrowid

            if order.items:
                for order_items in order.items:
                    items_insert_sql = f"""
                    INSERT INTO {order_items_table} (order_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(items_insert_sql, (order_id, order_items.item_id, order_items.amount))