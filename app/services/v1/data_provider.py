import os

DEBUG = False
ROOT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data/"
)

_warehouses = None
_locations = None
_transfers = None
_items = None
_item_lines = None
_item_groups = None
_item_types = None
_inventories = None
_suppliers = None
_orders = None
_shipments = None
_clients = None


def init():
    """Initialize all the data pools by loading from their respective models."""
    get_items()
    get_item_lines()
    get_item_groups()
    get_item_types()
    get_warehouses()
    get_locations()
    get_transfers()
    get_inventories()
    get_suppliers()
    get_clients()
    get_orders()
    get_shipments()


# Load data for each model
def get_items():
    from models.v1.items import Items

    global _items
    if _items is None:
        _items = Items(ROOT_PATH, DEBUG)


def get_item_lines():
    from models.v1.item_lines import ItemLines

    global _item_lines
    if _item_lines is None:
        _item_lines = ItemLines(ROOT_PATH, DEBUG)


def get_item_groups():
    from models.v1.item_groups import ItemGroups

    global _item_groups
    if _item_groups is None:
        _item_groups = ItemGroups(ROOT_PATH, DEBUG)


def get_item_types():
    from models.v1.item_types import ItemTypes

    global _item_types
    if _item_types is None:
        _item_types = ItemTypes(ROOT_PATH, DEBUG)


def get_warehouses():
    from models.v1.warehouses import Warehouses

    global _warehouses
    if _warehouses is None:
        _warehouses = Warehouses(ROOT_PATH, DEBUG)


def get_locations():
    from models.v1.locations import Locations

    global _locations
    if _locations is None:
        _locations = Locations(ROOT_PATH, DEBUG)


def get_transfers():
    from models.v1.transfers import Transfers

    global _transfers
    if _transfers is None:
        _transfers = Transfers(ROOT_PATH, DEBUG)


def get_clients():
    from models.v1.clients import Clients

    global _clients
    if _clients is None:
        _clients = Clients(ROOT_PATH, DEBUG)


def get_shipments():
    from models.v1.shipments import Shipments

    global _shipments
    if _shipments is None:
        _shipments = Shipments(ROOT_PATH, DEBUG)


def get_suppliers():
    from models.v1.suppliers import Suppliers

    global _suppliers
    if _suppliers is None:
        _suppliers = Suppliers(ROOT_PATH, DEBUG)


def get_inventories():
    from models.v1.inventories import Inventories

    global _inventories
    if _inventories is None:
        _inventories = Inventories(ROOT_PATH, DEBUG)


def get_orders():
    from models.v1.orders import Orders

    global _orders
    if _orders is None:
        _orders = Orders(ROOT_PATH, DEBUG)


# Fetching pools
def fetch_warehouse_pool():
    get_warehouses()
    return _warehouses


def fetch_location_pool():
    get_locations()
    return _locations


def fetch_transfer_pool():
    get_transfers()
    return _transfers


def fetch_item_pool():
    get_items()
    return _items


def fetch_item_line_pool():
    get_item_lines()
    return _item_lines


def fetch_item_group_pool():
    get_item_groups()
    return _item_groups


def fetch_item_type_pool():
    get_item_types()
    return _item_types


def fetch_inventory_pool():
    get_inventories()
    return _inventories


def fetch_supplier_pool():
    get_suppliers()
    return _suppliers


def fetch_order_pool():
    get_orders()
    return _orders


def fetch_client_pool():
    get_clients()
    return _clients


def fetch_shipment_pool():
    get_shipments()
    return _shipments
