import sqlite3
from contextlib import contextmanager
from typing import Type, TypeVar, List, Generator, Any, Tuple
from pydantic import BaseModel
from models.v2.endpoint_access import EndpointAccess
from models.v2.user import User
from models.v2.shipment import Shipment
from models.v2.warehouse import Warehouse as Warehouse
from models.v2.item import Item
from models.v2.client import Client
from models.v2.order import Order
from models.v2.inventory import Inventory
from models.v2.item_group import ItemGroup
from models.v2.item_line import ItemLine
from models.v2.item_type import ItemType
from models.v2.location import Location
from models.v2.supplier import Supplier
from models.v2.transfer import Transfer
from utils.globals import *
import os

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../app"))

T = TypeVar("T", bound=BaseModel)


class DatabaseService:
    def __init__(self, db_path: str = APP_PATH + "/database/database.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        self.create_orders_table(Order)
        self.create_clients_table(Client)
        self.create_items_table(Item)
        self.create_order_items_table(table_name=order_items_table)
        self.create_inventory_table(Inventory)
        self.create_item_group_table(ItemGroup)
        self.create_item_line_table(ItemLine)
        self.create_item_type_table(ItemType)
        self.create_location_table(Location)
        self.create_supplier_table(Supplier)
        self.create_transfer_table(Transfer)
        self.create_transfer_items_table(table_name=transfer_items_table)
        self.create_warehouse_table(Warehouse)
        self.create_shipment_table(Shipment)
        self.create_shipment_items_table(table_name=shipment_items_table)
        self.create_users_table(User)
        self.create_endpoint_access_table(EndpointAccess)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    @contextmanager
    def get_connection_without_close(
        self,
    ) -> Generator[sqlite3.Connection, None, None]:  
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        yield self.conn

    def stop_connection(self):  
        if self.conn:
            self.conn.close()
            self.conn = None

    def commit(self):  
        if self.conn:
            self.conn.commit()

    def commit_and_close(self):  
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def insert(self, model: T) -> T:  
        table_name = model.table_name()

        fields = model.__dict__

        primary_key_field = self.get_primary_key_column(table_name)

        if primary_key_field == "id":
            fields.pop(primary_key_field, None)
        else:
            if (
                self.execute_one(
                    f"SELECT * FROM {table_name} WHERE {primary_key_field} = ?",
                    (fields[primary_key_field],),
                )
                is not None
            ):
                return None

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.get_connection() as conn:
            cursor = conn.execute(insert_sql, values)

            if primary_key_field == "id":
                inserted_id = cursor.lastrowid
                model = model.model_copy(update={primary_key_field: inserted_id})
        return model

    def update(self, model: T, id: int) -> T:  
        table_name = model.table_name()
        primary_key_value = model.__dict__[self.get_primary_key_column(table_name)]
        fields = model.__dict__
        primary_key_field = self.get_primary_key_column(table_name)

        fields.pop(primary_key_field, None)
        columns = ", ".join(f"{key} = ?" for key in fields.keys())
        values = tuple(fields.values())
        update_sql = f"UPDATE {table_name} SET {columns} WHERE {primary_key_field} = ?"

        with self.get_connection() as conn:
            conn.execute(update_sql, values + (id,))

        model = model.model_copy(update={primary_key_field: primary_key_value})
        return model

    def delete(self, model: T, id: int) -> bool:  
        table_name = model.table_name()
        primary_key_field = self.get_primary_key_column(table_name)
        delete_sql = f"DELETE FROM {table_name} WHERE {primary_key_field} = ?"

        with self.get_connection() as conn:
            conn.execute(delete_sql, (id,))
        return True

    def get_primary_key_column(self, table_name: str) -> str:  
        query = f"PRAGMA table_info({table_name})"
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            columns = cursor.fetchall()

            for column in columns:
                if column[5] == 1:
                    return column[1]

        return "id"

    def get_all(self, model: Type[T]) -> List[T]:  
        table_name = model.table_name()
        select_sql = f"SELECT * FROM {table_name}"

        with self.get_connection() as conn:
            cursor = conn.execute(select_sql)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                row_dict = {col[0]: row[i] for i, col in enumerate(cursor.description)}
                result.append(model(**row_dict))

        return result

    def get(self, model: Type[T], id: int) -> T | None:  
        table_name = model.table_name()
        primary_key_field = self.get_primary_key_column(table_name)
        select_sql = f"SELECT * FROM {table_name} WHERE {primary_key_field} = ?"

        with self.get_connection() as conn:
            cursor = conn.execute(select_sql, (id,))
            row = cursor.fetchone()

            if row is None:
                return None

            row_dict = {col[0]: row[i] for i, col in enumerate(cursor.description)}
            return model(**row_dict)

    def execute_all(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[sqlite3.Row]:  
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def execute_one(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[sqlite3.Row]:  
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    def create_clients_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            zip_code TEXT,
            province TEXT,
            country TEXT,
            contact_name TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)

    def create_inventory_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_inventory = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            description TEXT NOT NULL,
            item_reference TEXT NOT NULL,
            total_on_hand INTEGER NOT NULL,
            total_expected INTEGER NOT NULL,
            total_ordered INTEGER NOT NULL,
            total_allocated INTEGER NOT NULL,
            total_available INTEGER NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (item_id) REFERENCES {Item.table_name()}(uid) ON DELETE CASCADE
        )
        """

        query_locations = f"""
        CREATE TABLE IF NOT EXISTS {inventory_locations_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            FOREIGN KEY (inventory_id) REFERENCES {Inventory.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES {Location.table_name()}(id) ON DELETE CASCADE
        )
        """

        with self.get_connection() as conn:  
            conn.execute(query_inventory)
            conn.execute(query_locations)

    def create_item_group_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_item_group = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        )
        """
        with self.get_connection() as conn:
            conn.execute(query_item_group)

    def create_item_line_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_item_line = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        )
        """
        with self.get_connection() as conn:
            conn.execute(query_item_line)

    def create_item_type_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_item_type = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        )
        """
        with self.get_connection() as conn:
            conn.execute(query_item_type)

    def create_items_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            uid TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            description TEXT,
            short_description TEXT,
            upc_code TEXT,
            model_number TEXT,
            commodity_code TEXT,
            item_line INTEGER,
            item_group INTEGER,
            item_type INTEGER,
            unit_purchase_quantity INTEGER,
            unit_order_quantity INTEGER,
            pack_order_quantity INTEGER,
            supplier_id INTEGER,
            supplier_code TEXT,
            supplier_part_number TEXT,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (item_line) REFERENCES {ItemLine.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (item_group) REFERENCES {ItemGroup.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (item_type) REFERENCES {ItemType.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (supplier_id) REFERENCES {Supplier.table_name()}(id) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)

    def create_location_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_location = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.table_name()}(id) ON DELETE CASCADE
        )
        """
        with self.get_connection() as conn:
            conn.execute(query_location)

    def create_orders_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            request_date TEXT NOT NULL,
            reference TEXT NOT NULL,
            reference_extra TEXT,
            order_status TEXT NOT NULL,
            notes TEXT,
            shipping_notes TEXT,
            picking_notes TEXT,
            warehouse_id INTEGER NOT NULL,
            ship_to INTEGER,
            bill_to INTEGER,
            shipment_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            total_discount REAL NOT NULL,
            total_tax REAL NOT NULL,
            total_surcharge REAL NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (warehouse_id) REFERENCES {Warehouse.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (ship_to) REFERENCES {Client.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (bill_to) REFERENCES {Client.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (shipment_id) REFERENCES {Shipment.table_name()}(id) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:  
            conn.execute(query)

    def create_order_items_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES {Order.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES {Item.table_name()}(uid) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)

    def create_shipment_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_shipment = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            request_date TEXT NOT NULL,
            shipment_date TEXT NOT NULL,
            shipment_type TEXT NOT NULL,
            shipment_status TEXT NOT NULL,
            notes TEXT,
            carrier_code TEXT NOT NULL,
            carrier_description TEXT NOT NULL,
            service_code TEXT NOT NULL,
            payment_type TEXT NOT NULL,
            transfer_mode TEXT NOT NULL,
            total_package_count INTEGER NOT NULL,
            total_package_weight REAL NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES {Order.table_name()}(id) ON DELETE CASCADE
        )
        """
        with self.get_connection() as conn:  
            conn.execute(query_shipment)

    def create_shipment_items_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            item_uid TEXT NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY (shipment_id) REFERENCES {Shipment.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (item_uid) REFERENCES {Item.table_name()}(uid) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)

    def create_supplier_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_supplier = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            address_extra TEXT,
            city TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            province TEXT,
            country TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            phonenumber TEXT NOT NULL,
            reference TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        )
        """
        with self.get_connection() as conn:  
            conn.execute(query_supplier)

    def create_transfer_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_transfer = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            transfer_from INTEGER,
            transfer_to INTEGER,
            transfer_status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (transfer_from) REFERENCES {Location.table_name()}(id) ON DELETE CASCADE
            FOREIGN KEY (transfer_to) REFERENCES {Location.table_name()}(id) ON DELETE CASCADE
        )
        """
        with self.get_connection() as conn:  
            conn.execute(query_transfer)

    def create_transfer_items_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transfer_id INTEGER NOT NULL,
            item_uid TEXT NOT NULL,
            amount INTEGER NOT NULL,
            FOREIGN KEY (transfer_id) REFERENCES {Transfer.table_name()}(id) ON DELETE CASCADE,
            FOREIGN KEY (item_uid) REFERENCES {Item.table_name()}(uid) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:
            conn.execute(query)

    def create_warehouse_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_warehouse = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            zip TEXT NOT NULL,
            city TEXT NOT NULL,
            province TEXT,
            country TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            contact_email TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            is_archived BOOLEAN DEFAULT 0
        )
        """
        with self.get_connection() as conn:  
            conn.execute(query_warehouse)

    def create_users_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_users = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT UNIQUE NOT NULL,
            app TEXT NOT NULL,
            full_access BOOLEAN NOT NULL,
            is_archived BOOLEAN DEFAULT 0
        )
        """

        with self.get_connection() as conn:
            conn.execute(query_users)

    def create_endpoint_access_table(
        self, model: Type[BaseModel] | None = None, table_name: str | None = None
    ):
        if model is not None:  
            table_name = model.table_name()

        query_endpoint_access = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL,
            full BOOLEAN NOT NULL,
            can_get BOOLEAN NOT NULL,
            can_post BOOLEAN NOT NULL,
            can_put BOOLEAN NOT NULL,
            can_delete BOOLEAN NOT NULL,
            FOREIGN KEY (user_id) REFERENCES {User.table_name()} (id)
        )
        """

        with self.get_connection() as conn:  
            conn.execute(query_endpoint_access)
