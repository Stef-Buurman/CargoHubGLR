from services import data_provider_v2
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
    # for client in data_provider_v2.fetch_client_pool().get_clients():
    #         data_provider_v2.fetch_client_pool().insert_client(client)

    # for inventory in data_provider_v2.fetch_inventory_pool().get_inventories():
    #     data_provider_v2.fetch_inventory_pool().insert_inventory(inventory)
    
    # for item in data_provider_v2.fetch_item_pool().get_items():
    #     data_provider_v2.fetch_item_pool().insert_item(item)
    
    # for item_group in data_provider_v2.fetch_item_group_pool().get_item_groups():
    #     data_provider_v2.fetch_item_group_pool().insert_item_group(item_group)
    
    # for item_line in data_provider_v2.fetch_item_line_pool().get_item_lines():
    #     data_provider_v2.fetch_item_line_pool().insert_item_line(item_line)
    
    # for item_type in data_provider_v2.fetch_item_type_pool().get_item_types():
    #     data_provider_v2.fetch_item_type_pool().insert_item_type(item_type)

    # for location in data_provider_v2.fetch_location_pool().get_locations():
    #     data_provider_v2.fetch_location_pool().insert_location(location)

    for order in data_provider_v2.fetch_order_pool().get_orders():
        data_provider_v2.fetch_order_pool().insert_order(order)

    # for shipment in data_provider_v2.fetch_shipment_pool().get_shipments():
    #     data_provider_v2.fetch_shipment_pool().insert_shipment(shipment)

    # for supplier in data_provider_v2.fetch_supplier_pool().get_suppliers():
    #     data_provider_v2.fetch_supplier_pool().insert_supplier(supplier)
    
    # for transfer in data_provider_v2.fetch_transfer_pool().get_transfers():
    #     data_provider_v2.fetch_transfer_pool().insert_transfer(transfer)

    # for warehouse in data_provider_v2.fetch_warehouse_pool().get_warehouses():
    #     data_provider_v2.fetch_warehouse_pool().insert_warehouse(Warehouse(
    #     code=warehouse.code,
    #     name=warehouse.name,
    #     address=warehouse.address,
    #     zip=warehouse.zip,
    #     city=warehouse.city,
    #     province=warehouse.province,
    #     country=warehouse.country,
    #     contact_name=warehouse.contact.name,
    #     contact_phone=warehouse.contact.phone,
    #     contact_email=warehouse.contact.email
    # ))

    elapsed_time = time.time() - start_time

    elapsed_minutes = elapsed_time / 60

    print(f"The script ran for {elapsed_minutes:.2f} minutes.")