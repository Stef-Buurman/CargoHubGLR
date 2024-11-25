import json
from typing import List
from models.v2.order import Order
from models.base import Base
from services.data_provider_v2 import fetch_inventory_pool
from models.v2.ItemInObject import ItemInObject
from utils.globals import *
from services.database_service import DB


class OrderService(Base):
    def __init__(self, is_debug=False):
        self.db = DB
        self.load(is_debug)

    def get_orders(self) -> List[Order]:
        return self.db.get_all(Order)

    def get_order(self, order_id: int) -> Order | None:
        return self.db.get(Order, order_id)

    def get_items_in_order(self, order_id: int) -> List[ItemInObject]:
        query = "SELECT item_id, amount FROM order_items WHERE order_id = ?"
        result = self.db.execute_all(query, (order_id,))

        items = []
        for row in result:
            item = ItemInObject(item_id=row[0], amount=row[1])
            items.append(item)
        return items

    def get_orders_in_shipment(self, shipment_id: int) -> List[Order]:
        result = []
        for x in self.data:
            if x.shipment_id == shipment_id:
                result.append(x.id)
        return result

    def get_orders_for_shipments(self, shipment_id: int) -> List[Order]:
        result = []
        for order in self.data:
            if order.shipment_id == shipment_id:
                result.append(order)
        return result

    def get_orders_for_client(self, client_id: str) -> List[Order]:
        result = []
        for order in self.data:
            if order.ship_to == client_id or order.bill_to == client_id:
                result.append(order)
        return result

    def add_order(self, order: Order, closeConnection: bool = True) -> Order:
        table_name = order.table_name()

        order.created_at = self.get_timestamp()
        order.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(order).items():
            if key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"""INSERT INTO {
            table_name} ({columns}) VALUES ({placeholders})"""

        with self.db.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)
            order_id = cursor.lastrowid

            if order.items:
                for order_items in order.items:
                    items_insert_sql = f"""
                    INSERT INTO {order_items_table} (order_id, item_id, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (order_id, order_items.item_id, order_items.amount),
                    )

        if closeConnection:
            self.db.commit_and_close()
        return order

    def update_order(
        self, order_id: int, order: Order, closeConnection: bool = True
    ) -> Order | None:
        table_name = order.table_name()

        order.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(order).items():
            if key != "items":
                fields[key] = value

        set_clause = ", ".join(f"{key} = ?" for key in fields if key != "id")
        values = tuple(fields[key] for key in fields if key != "id") + (order.id,)

        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

        with self.db.get_connection_without_close() as conn:
            conn.execute(update_sql, values)

            if order.items:
                delete_items_sql = f"""DELETE FROM {
                    order_items_table} WHERE order_id = ?"""
                conn.execute(delete_items_sql, (order.id,))

                for order_items in order.items:
                    items_insert_sql = f"""
                    INSERT INTO {order_items_table} (order_id, item_id, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (order.id, order_items.item_id, order_items.amount),
                    )

        if closeConnection:
            self.db.commit_and_close()

        return order

    def update_items_in_order(
        self, order_id: int, items: List[ItemInObject]
    ) -> Order | None:
        current_items = self.get_items_in_order(order_id)

        for current_item in current_items:
            found = False
            for updated_item in items:
                if current_item.item_id == updated_item.item_id:
                    found = True
                    break
            if not found:
                delete_query = (
                    "DELETE FROM order_items WHERE order_id = ? AND item_id = ?"
                )
                self.db.execute_all(delete_query, (order_id, current_item.item_id))

        for updated_item in items:
            found = False
            for current_item in current_items:
                if current_item.item_id == updated_item.item_id:
                    found = True
                    break

            if not found:
                insert_query = """
                INSERT INTO order_items (order_id, item_id, amount) VALUES (?, ?, ?)
                """
                self.db.execute_all(
                    insert_query, (order_id, updated_item.item_id, updated_item.amount)
                )

        order = self.get_order(order_id)
        order.updated_at = self.get_timestamp()
        self.update_order(order_id, order)

        return order

    def update_orders_in_shipment(
        self, shipment_id: int, orders: List[Order]
    ) -> List[Order]:
        packed_orders = self.get_orders_in_shipment(shipment_id)
        for x in packed_orders:
            if x not in orders:
                order = self.get_order(x)
                order.shipment_id = -1
                order.order_status = "Scheduled"
                self.update_order(order.id, order)

        for order in orders:
            order.shipment_id = shipment_id
            order.order_status = "Packed"
            self.update_order(order.id, order)

        return orders

    def remove_order(self, order_id: int, closeConnection: bool = True) -> bool:
        return self.db.delete(Order, order_id, closeConnection)

    def load(self, is_debug: bool, orders: List[Order] | None = None):
        if is_debug and orders is not None:
            self.data = orders
        else:
            self.data = self.db.get_all(Order)

    def insert_order(self, order: Order, closeConnection: bool = True) -> Order:
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

        insert_sql = f"""INSERT INTO {
            table_name} ({columns}) VALUES ({placeholders})"""

        with self.db.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)
            order_id = cursor.lastrowid

            if order.items:
                for order_items in order.items:
                    items_insert_sql = f"""
                    INSERT INTO {order_items_table} (order_id, item_id, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (order_id, order_items.item_id, order_items.amount),
                    )

        if closeConnection:
            self.db.commit_and_close()
        return order
