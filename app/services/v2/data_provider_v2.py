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


def get_items():
    from .model_services.item_services import ItemService

    global _items
    if _items is None:
        _items = ItemService()


def get_item_lines():
    from .model_services.item_line_service import ItemLineService

    global _item_lines
    if _item_lines is None:
        _item_lines = ItemLineService()


def get_item_groups():
    from .model_services.item_group_service import ItemGroupService

    global _item_groups
    if _item_groups is None:
        _item_groups = ItemGroupService()


def get_item_types():
    from .model_services.item_type_service import ItemTypeService

    global _item_types
    if _item_types is None:
        _item_types = ItemTypeService()


def get_warehouses():
    from .model_services.warehouse_service import WarehouseService

    global _warehouses
    if _warehouses is None:
        _warehouses = WarehouseService()


def get_locations():
    from .model_services.location_service import LocationService

    global _locations
    if _locations is None:
        _locations = LocationService()


def get_transfers():
    from .model_services.transfer_service import TransferService

    global _transfers
    if _transfers is None:
        _transfers = TransferService()


def get_clients():
    from .model_services.client_service import ClientService

    global _clients
    if _clients is None:
        _clients = ClientService()


def get_shipments():
    from .model_services.shipment_service import ShipmentService

    global _shipments
    if _shipments is None:
        _shipments = ShipmentService()


def get_suppliers():
    from .model_services.suppliers_service import SupplierService

    global _suppliers
    if _suppliers is None:
        _suppliers = SupplierService()


def get_inventories():
    from .model_services.inventory_service import InventoryService

    global _inventories
    if _inventories is None:
        _inventories = InventoryService()


def get_orders():
    from .model_services.order_service import OrderService

    global _orders
    if _orders is None:
        _orders = OrderService()


def get_users():
    from .model_services.user_service import UserService

    global _users
    if _users is None:
        _users = UserService()


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


def fetch_user_pool():
    get_users()
    return _users
