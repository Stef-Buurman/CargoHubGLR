from fastapi import APIRouter

from api.v1.endpoints.item import item_router
from api.v1.endpoints.item_line import item_line_router
from api.v1.endpoints.item_group import item_group_router
from api.v1.endpoints.item_type import item_type_router
from api.v1.endpoints.shipment import shipment_router
from api.v1.endpoints.client import client_router
from api.v1.endpoints.warehouse import warehouse_router
from api.v1.endpoints.inventory import inventory_router
from api.v1.endpoints.order import order_router
from api.v1.endpoints.supplier import supplier_router
from api.v1.endpoints.transfer import transfer_router
from api.v1.endpoints.location import location_router

routers = APIRouter()

router_list = [
    item_router,
    item_line_router,
    item_group_router,
    item_type_router,
    shipment_router,
    client_router,
    warehouse_router,
    inventory_router,
    order_router,
    supplier_router,
    transfer_router,
    location_router,
]


for router in router_list:
    routers.include_router(router)
