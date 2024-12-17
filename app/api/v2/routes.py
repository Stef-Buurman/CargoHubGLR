from fastapi import APIRouter

from api.v2.endpoints.item import item_router_v2
from api.v2.endpoints.warehouse import warehouse_router_v2
from api.v2.endpoints.location import location_router_v2
from api.v2.endpoints.transfer import transfer_router_v2
from api.v2.endpoints.inventory import inventory_router_v2
from api.v2.endpoints.Item_group import item_group_router_v2
from api.v2.endpoints.item_line import item_line_router_v2
from api.v2.endpoints.item_type import item_type_router_v2
from api.v2.endpoints.shipment import shipment_router_v2
from api.v2.endpoints.client import client_router_v2
from api.v2.endpoints.supplier import supplier_router_v2
from api.v2.endpoints.orders import order_router_v2

routers = APIRouter()

router_list = [
    item_router_v2,
    warehouse_router_v2,
    location_router_v2,
    transfer_router_v2,
    inventory_router_v2,
    item_group_router_v2,
    item_line_router_v2,
    item_type_router_v2,
    shipment_router_v2,
    client_router_v2,
    supplier_router_v2,
    order_router_v2,
]


for router in router_list:
    routers.include_router(router)
