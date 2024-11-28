from typing import List
from models.v2.order import Order
from models.base import Base
from models.v2.ItemInObject import ItemInObject
from utils.globals import *
from services.database_service import DB


class OrderService(Base):
    def __init__(self, is_debug: bool = False, orders: List[Order] = None):
        self.db = DB
        self.load(is_debug, orders)

    def get_orders(self) -> List[Order]:
        all_orders = self.db.get_all(Order)
        order_ids = [order.id for order in all_orders]

        with self.db.get_connection() as conn:
            query = f"SELECT item_id, amount, order_id FROM {order_items_table} WHERE order_id IN ({', '.join(map(str, order_ids))})"
            cursor = conn.execute(query)
            all_order_items = cursor.fetchall()

        order_items_map = {}
        for row in all_order_items:
            if row[2] not in order_items_map:
                order_items_map[row[2]] = []
            order_items_map[row[2]].append(ItemInObject(item_id=row[0], amount=row[1]))

        for order in all_orders:
            order.items = order_items_map.get(order.id, [])

        return all_orders

    def get_order(self, order_id: int) -> Order | None:
        for order in self.data:
            if order.id == order_id:
                return order

        with self.db.get_connection() as conn:
            query = f"SELECT * FROM {Order.table_name()} WHERE id = {order_id}"
            cursor = conn.execute(query)
            order = cursor.fetchone()
            if order:
                query_items = f"SELECT item_id, amount, order_id FROM {order_items_table} WHERE order_id = {order_id}"
                cursor = conn.execute(query_items)
                all_order_items = cursor.fetchall()
                order["items"] = all_order_items
                return Order(**order)
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
            order.id = order_id

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
        self.data.append(order)
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

        for i in range(len(self.data)):
            if self.data[i].id == order_id:
                self.data[i] = order
        return order

    def update_items_in_order(
        self, order_id: int, items: List[ItemInObject]
    ) -> Order | None:
        order = self.get_order(order_id)
        order.items = items
        return self.update_order(order_id, order)

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
        for order in self.data:
            if order.id == order_id:
                if self.db.delete(Order, order_id, closeConnection):
                    with self.db.get_connection_without_close() as conn:
                        conn.execute(
                            f"DELETE FROM {order_items_table} WHERE order_id = ?",
                            (order_id,),
                        )
                    if closeConnection:
                        self.db.commit_and_close()
                    self.data.remove(order)
                break
        return True

    def load(self, is_debug: bool, orders: List[Order] | None = None):
        if is_debug and orders is not None:
            self.data = orders
        else:
            self.data = self.get_orders()
