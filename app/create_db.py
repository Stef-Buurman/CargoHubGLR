from typing import TypeVar

from pydantic import BaseModel
from models.v2.user import User
from services.v1 import data_provider
from services.v2 import data_provider_v2
from services.v2.database_service import DatabaseService
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
import time

T = TypeVar("T", bound=BaseModel)

USERS = [
    {
        "api_key": "test_api_key",
        "app": "Integration_Tests",
        "endpoint_access": {"full": True},
    },
    {
        "api_key": "a1b2c3d4e5",
        "app": "CargoHUB Dashboard 1",
        "endpoint_access": {"full": True},
    },
    {
        "api_key": "f6g7h8i9j0",
        "app": "CargoHUB Dashboard 2",
        "endpoint_access": {
            "full": False,
            "warehouses": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "locations": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "transfers": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "items": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_lines": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_groups": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_types": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "suppliers": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "orders": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "clients": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "shipments": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
        },
    },
]


db_service = DatabaseService()

def insert(model: T, closeConnection: bool = True) -> T:  # pragma: no cover
        table_name = model.table_name()

        fields = model.__dict__

        primary_key_field = db_service.get_primary_key_column(table_name)

        if primary_key_field == "id":
            fields.pop(primary_key_field, None)
        else:
            if (
                db_service.execute_one(
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

        with db_service.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)

            if primary_key_field == "id":
                inserted_id = cursor.lastrowid
                model = model.model_copy(update={primary_key_field: inserted_id})

        if closeConnection:
            db_service.commit_and_close()
        return model

if __name__ == "__main__":
    start_time = time.time()

    data_provider_v2.init()
    data_provider.init()

    amount_before_closing = 500

    for user in USERS:
        endpoint_access = user["endpoint_access"].copy()
        del endpoint_access["full"]
        data_provider_v2.fetch_user_pool().add_user(
            user["api_key"],
            user["app"],
            user["endpoint_access"]["full"],
            endpoint_access,
        )

    count = 0
    all_clients = data_provider.fetch_client_pool().get_clients()
    for client in all_clients:
        count += 1
        x = Client(**client)
        if count % amount_before_closing == 0 or count == len(all_clients):
            insert(x)
        else:
            insert(x, False)

    count = 0
    all_inventories = data_provider.fetch_inventory_pool().get_inventories()
    for inventory in all_inventories:
        count += 1

        inventory = Inventory(**inventory)

        table_name = inventory.table_name()

        fields = data_provider_v2.fetch_inventory_pool().get_key_values_of_inventory(inventory)

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with db_service.get_connection_without_close() as conn:
            cursor_inventory = conn.execute(insert_sql, values)
            inventory.id = cursor_inventory.lastrowid

            if inventory.locations:
                for location_id in inventory.locations:
                    location_insert_sql = f"""
                    INSERT INTO {inventory_locations_table} (inventory_id, location_id)
                    VALUES (?, ?)
                    """
                    conn.execute(location_insert_sql, (inventory.id, location_id))

        if count % amount_before_closing == 0 or count == len(all_inventories):
            db_service.commit_and_close()

        # if count % amount_before_closing == 0 or count == len(all_inventories):
        #     data_provider_v2.fetch_inventory_pool().add_inventory(
        #         Inventory(**inventory)
        #     )
        # else:
        #     data_provider_v2.fetch_inventory_pool().add_inventory(
        #         Inventory(**inventory), False
        #     )

    count = 0
    all_items = data_provider.fetch_item_pool().get_items()
    for item in all_items:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_items):
            insert(Item(**item))
        else:
            insert(Item(**item), False)

    count = 0
    all_item_groups = data_provider.fetch_item_group_pool().get_item_groups()
    for item_group in all_item_groups:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_groups):
            insert(
                ItemGroup(**item_group)
            )
        else:
            insert(
                ItemGroup(**item_group), False
            )

    count = 0
    all_item_lines = data_provider.fetch_item_line_pool().get_item_lines()
    for item_line in all_item_lines:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_lines):
            insert(ItemLine(**item_line))
        else:
            insert(
                ItemLine(**item_line), False
            )

    count = 0
    all_item_types = data_provider.fetch_item_type_pool().get_item_types()
    for item_type in all_item_types:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_types):
            insert(ItemType(**item_type))
        else:
            insert(
                ItemType(**item_type), False
            )

    count = 0
    all_shipments = data_provider.fetch_shipment_pool().get_shipments()
    for shipment in all_shipments:
        count += 1

        shipment = Shipment(**shipment)

        table_name = shipment.table_name()

        fields = {}
        for key, value in vars(shipment).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with db_service.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)
            shipment_id = cursor.lastrowid
            shipment.id = shipment_id

            if shipment.items:
                for shipment_items in shipment.items:
                    items_insert_sql = f"""
                    INSERT INTO {shipment_items_table} (shipment_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (shipment_id, shipment_items.item_id, shipment_items.amount),
                    )

        if count % amount_before_closing == 0 or count == len(all_shipments):
            db_service.commit_and_close()

        # if count % amount_before_closing == 0 or count == len(all_shipments):
        #     data_provider_v2.fetch_shipment_pool().add_shipment(Shipment(**shipment))
        # else:
        #     data_provider_v2.fetch_shipment_pool().add_shipment(
        #         Shipment(**shipment), False
        #     )

    count = 0
    all_suppliers = data_provider.fetch_supplier_pool().get_suppliers()
    for supplier in all_suppliers:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_suppliers):
            insert(Supplier(**supplier))
        else:
            insert(
                Supplier(**supplier), False
            )

    count = 0
    all_transfers = data_provider.fetch_transfer_pool().get_transfers()
    for transfer in all_transfers:
        count += 1

        transfer = Transfer(**transfer)

        table_name = transfer.table_name()

        fields = {}
        for key, value in vars(transfer).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with db_service.get_connection_without_close() as conn:
            cursor = conn.execute(insert_sql, values)
            transfer_id = cursor.lastrowid
            transfer.id = transfer_id

            if transfer.items:
                for transfer_items in transfer.items:
                    items_insert_sql = f"""
                    INSERT INTO {transfer_items_table} (transfer_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (transfer_id, transfer_items.item_id, transfer_items.amount),
                    )

        if count % amount_before_closing == 0 or count == len(all_transfers):
            db_service.commit_and_close()

        # if count % amount_before_closing == 0 or count == len(all_transfers):
        #     data_provider_v2.fetch_transfer_pool().add_transfer(Transfer(**transfer))
        # else:
        #     data_provider_v2.fetch_transfer_pool().add_transfer(
        #         Transfer(**transfer), False
        #     )

    count = 0
    all_warehouses = data_provider.fetch_warehouse_pool().get_warehouses()
    for warehouse in all_warehouses:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_warehouses):
            insert(
                Warehouse(
                    code=warehouse["code"],
                    name=warehouse["name"],
                    address=warehouse["address"],
                    zip=warehouse["zip"],
                    city=warehouse["city"],
                    province=warehouse["province"],
                    country=warehouse["country"],
                    contact_name=warehouse["contact"]["name"],
                    contact_phone=warehouse["contact"]["phone"],
                    contact_email=warehouse["contact"]["email"],
                )
            )
        else:
            insert(
                Warehouse(
                    code=warehouse["code"],
                    name=warehouse["name"],
                    address=warehouse["address"],
                    zip=warehouse["zip"],
                    city=warehouse["city"],
                    province=warehouse["province"],
                    country=warehouse["country"],
                    contact_name=warehouse["contact"]["name"],
                    contact_phone=warehouse["contact"]["phone"],
                    contact_email=warehouse["contact"]["email"],
                ),
                False,
            )

    count = 0
    all_locations = data_provider.fetch_location_pool().get_locations()
    for location in all_locations:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_locations):
            insert(Location(**location))
        else:
            insert(
                Location(**location), False
            )

    count = 0
    all_orders = data_provider.fetch_order_pool().get_orders()
    for order in all_orders:
        count += 1

        order = Order(**order)

        table_name = order.table_name()

        fields = {}
        for key, value in vars(order).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"""INSERT INTO {
            table_name} ({columns}) VALUES ({placeholders})"""

        with db_service.get_connection_without_close() as conn:
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

        if count % amount_before_closing == 0 or count == len(all_orders):
            db_service.commit_and_close()


        # if count % amount_before_closing == 0 or count == len(all_orders):
        #     data_provider_v2.fetch_order_pool().add_order(Order(**order))
        # else:
        #     data_provider_v2.fetch_order_pool().add_order(Order(**order), False)

    elapsed_time = time.time() - start_time

    elapsed_seconds = elapsed_time

    print(f"The script ran for {elapsed_seconds:.2f} seconds.")
