import os

DEBUG = False
ROOT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data/"
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
    from .ItemServices import ItemService

    global _items
    _items = ItemService(ROOT_PATH, DEBUG)


def get_item_lines():
    from models.item_lines import ItemLines

    global _item_lines
    _item_lines = ItemLines(ROOT_PATH, DEBUG)


def get_item_groups():
    from models.item_groups import ItemGroups

    global _item_groups
    _item_groups = ItemGroups(ROOT_PATH, DEBUG)


def get_item_types():
    from models.item_types import ItemTypes

    global _item_types
    _item_types = ItemTypes(ROOT_PATH, DEBUG)


def get_warehouses():
    from .WarehouseService import WarehouseService

    global _warehouses
    _warehouses = WarehouseService(ROOT_PATH, DEBUG)


def get_locations():
    from .LocationService import LocationService

    global _locations
    _locations = LocationService(ROOT_PATH, DEBUG)


def get_transfers():
    from .TransferService import TransferService

    global _transfers
    _transfers = TransferService(ROOT_PATH, DEBUG)


def get_clients():
    from models.clients import Clients

    global _clients
    _clients = Clients(ROOT_PATH, DEBUG)


def get_shipments():
    from models.shipments import Shipments

    global _shipments
    _shipments = Shipments(ROOT_PATH, DEBUG)


def get_suppliers():
    from models.suppliers import Suppliers

    global _suppliers
    _suppliers = Suppliers(ROOT_PATH, DEBUG)


def get_inventories():
    from models.inventories import Inventories

    global _inventories
    _inventories = Inventories(ROOT_PATH, DEBUG)


def get_orders():
    from models.orders import Orders

    global _orders
    _orders = Orders(ROOT_PATH, DEBUG)


# Fetching pools
def fetch_warehouse_pool():
    if _warehouses is None:
        get_warehouses()
    return _warehouses


def fetch_location_pool():
    if _locations is None:
        get_locations()
    return _locations


def fetch_transfer_pool():
    if _transfers is None:
        get_transfers()
    return _transfers


def fetch_item_pool():
    if _items is None:
        get_items()
    return _items


def fetch_item_line_pool():
    if _item_lines is None:
        get_item_lines()
    return _item_lines


def fetch_item_group_pool():
    if _item_groups is None:
        get_item_groups()
    return _item_groups


def fetch_item_type_pool():
    if _item_types is None:
        get_item_types()
    return _item_types


def fetch_inventory_pool():
    if _inventories is None:
        get_inventories()
    return _inventories


def fetch_supplier_pool():
    if _suppliers is None:
        get_suppliers()
    return _suppliers


def fetch_order_pool():
    if _orders is None:
        get_orders()
    return _orders


def fetch_client_pool():
    if _clients is None:
        get_clients()
    return _clients


def fetch_shipment_pool():
    if _shipments is None:
        get_shipments()
    return _shipments
