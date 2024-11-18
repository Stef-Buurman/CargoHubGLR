from services import data_provider, data_provider_v2
from services.database_service import DatabaseService
from models.v2.shipment import Shipment
from models.v2.warehouse import WarehouseDB as Warehouse
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

if __name__ == "__main__":
    start_time = time.time()
    db_service = DatabaseService()

    data_provider_v2.init()
    data_provider.init()

    amount_before_closing = 500

    count = 0
    all_clients = data_provider.fetch_client_pool().get_clients()
    for client in all_clients:
        count += 1

        if count % amount_before_closing == 0 or count == len(all_clients):
            data_provider_v2.fetch_client_pool().insert_client(Client(**client))
        else:
            data_provider_v2.fetch_client_pool().insert_client(Client(**client), False)

    count = 0
    all_items = data_provider.fetch_inventory_pool().get_inventories()
    for inventory in all_items:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_items):
            data_provider_v2.fetch_inventory_pool().insert_inventory(
                Inventory(**inventory)
            )
        else:
            data_provider_v2.fetch_inventory_pool().insert_inventory(
                Inventory(**inventory), False
            )

    count = 0
    all_items = data_provider.fetch_item_pool().get_items()
    for item in all_items:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_items):
            data_provider_v2.fetch_item_pool().insert_item(Item(**item))
        else:
            data_provider_v2.fetch_item_pool().insert_item(Item(**item), False)

    count = 0
    all_item_groups = data_provider.fetch_item_group_pool().get_item_groups()
    for item_group in all_item_groups:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_groups):
            data_provider_v2.fetch_item_group_pool().insert_item_group(
                ItemGroup(**item_group)
            )
        else:
            data_provider_v2.fetch_item_group_pool().insert_item_group(
                ItemGroup(**item_group), False
            )

    count = 0
    all_item_lines = data_provider.fetch_item_line_pool().get_item_lines()
    for item_line in all_item_lines:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_lines):
            data_provider_v2.fetch_item_line_pool().insert_item_line(
                ItemLine(**item_line)
            )
        else:
            data_provider_v2.fetch_item_line_pool().insert_item_line(
                ItemLine(**item_line), False
            )

    count = 0
    all_item_types = data_provider.fetch_item_type_pool().get_item_types()
    for item_type in all_item_types:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_item_types):
            data_provider_v2.fetch_item_type_pool().insert_item_type(
                ItemType(**item_type)
            )
        else:
            data_provider_v2.fetch_item_type_pool().insert_item_type(
                ItemType(**item_type), False
            )

    count = 0
    all_shipments = data_provider.fetch_shipment_pool().get_shipments()
    for shipment in all_shipments:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_shipments):
            data_provider_v2.fetch_shipment_pool().insert_shipment(Shipment(**shipment))
        else:
            data_provider_v2.fetch_shipment_pool().insert_shipment(
                Shipment(**shipment), False
            )

    count = 0
    all_suppliers = data_provider.fetch_supplier_pool().get_suppliers()
    for supplier in all_suppliers:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_suppliers):
            data_provider_v2.fetch_supplier_pool().insert_supplier(Supplier(**supplier))
        else:
            data_provider_v2.fetch_supplier_pool().insert_supplier(
                Supplier(**supplier), False
            )

    count = 0
    all_transfers = data_provider.fetch_transfer_pool().get_transfers()
    for transfer in all_transfers:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_transfers):
            data_provider_v2.fetch_transfer_pool().insert_transfer(Transfer(**transfer))
        else:
            data_provider_v2.fetch_transfer_pool().insert_transfer(
                Transfer(**transfer), False
            )

    count = 0
    all_warehouses = data_provider.fetch_warehouse_pool().get_warehouses()
    for warehouse in all_warehouses:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_warehouses):
            data_provider_v2.fetch_warehouse_pool().insert_warehouse(
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
            data_provider_v2.fetch_warehouse_pool().insert_warehouse(
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
            data_provider_v2.fetch_location_pool().insert_location(Location(**location))
        else:
            data_provider_v2.fetch_location_pool().insert_location(
                Location(**location), False
            )

    count = 0
    all_orders = data_provider.fetch_order_pool().get_orders()
    for order in all_orders:
        count += 1
        if count % amount_before_closing == 0 or count == len(all_orders):
            data_provider_v2.fetch_order_pool().insert_order(Order(**order))
        else:
            data_provider_v2.fetch_order_pool().insert_order(Order(**order), False)

    elapsed_time = time.time() - start_time

    elapsed_seconds = elapsed_time

    print(f"The script ran for {elapsed_seconds:.2f} seconds.")
