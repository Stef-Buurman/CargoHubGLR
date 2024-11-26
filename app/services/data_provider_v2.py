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
_users = None


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
    get_users()


# Load data for each model
def get_items():
    from .item_services import ItemService

    global _items
    _items = ItemService(DEBUG)


def get_item_lines():
    from .item_line_service import ItemLineService

    global _item_lines
    _item_lines = ItemLineService(ROOT_PATH, DEBUG)


def get_item_groups():
    from .item_group_service import ItemGroupService

    global _item_groups
    _item_groups = ItemGroupService(DEBUG)


def get_item_types():
    from .item_type_service import ItemTypeService

    global _item_types
    _item_types = ItemTypeService(ROOT_PATH, DEBUG)


def get_warehouses():
    from .warehouse_service import WarehouseService

    global _warehouses
    _warehouses = WarehouseService(DEBUG)


def get_locations():
    from .location_service import LocationService

    global _locations
    _locations = LocationService(DEBUG)


def get_transfers():
    from .transfer_service import TransferService

    global _transfers
    _transfers = TransferService(DEBUG)


def get_clients():
    from .client_service import ClientService

    global _clients
    _clients = ClientService(DEBUG)


def get_shipments():
    from .shipment_service import ShipmentService

    global _shipments
    _shipments = ShipmentService(ROOT_PATH, DEBUG)


def get_suppliers():
    from .suppliers_service import SupplierService

    global _suppliers
    _suppliers = SupplierService(DEBUG)


def get_inventories():
    from .inventory_service import InventoryService

    global _inventories
    _inventories = InventoryService(DEBUG)


def get_orders():
    from .order_service import OrderService

    global _orders
    _orders = OrderService(DEBUG)


def get_users():
    from .user_service import UserService

    global _users
    _users = UserService(DEBUG)


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


def fetch_user_pool():
    if _users is None:
        get_users()
    return _users
