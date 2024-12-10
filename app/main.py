import os
from fastapi import FastAPI
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


import uvicorn

app = FastAPI()

v1_url = "/api/v1"
v2_url = "/api/v2"

app.include_router(client_router, prefix=v1_url + "/clients")
app.include_router(inventory_router, prefix=v1_url + "/inventories")
app.include_router(item_group_router, prefix=v1_url + "/item_groups")
app.include_router(item_line_router, prefix=v1_url + "/item_lines")
app.include_router(item_type_router, prefix=v1_url + "/item_types")
app.include_router(item_router, prefix=v1_url + "/items")
app.include_router(location_router, prefix=v1_url + "/locations")
app.include_router(order_router, prefix=v1_url + "/orders")
app.include_router(shipment_router, prefix=v1_url + "/shipments")
app.include_router(supplier_router, prefix=v1_url + "/suppliers")
app.include_router(transfer_router, prefix=v1_url + "/transfers")
app.include_router(warehouse_router, prefix=v1_url + "/warehouses")

app.include_router(client_router_v2, prefix=v2_url + "/clients")
app.include_router(inventory_router_v2, prefix=v2_url + "/inventories")
app.include_router(item_group_router_v2, prefix=v2_url + "/item_groups")
app.include_router(item_line_router_v2, prefix=v2_url + "/item_lines")
app.include_router(item_type_router_v2, prefix=v2_url + "/item_types")
app.include_router(item_router_v2, prefix=v2_url + "/items")
app.include_router(location_router_v2, prefix=v2_url + "/locations")
app.include_router(order_router_v2, prefix=v2_url + "/orders")
app.include_router(shipment_router_v2, prefix=v2_url + "/shipments")
app.include_router(supplier_router_v2, prefix=v2_url + "/suppliers")
app.include_router(transfer_router_v2, prefix=v2_url + "/transfers")
app.include_router(warehouse_router_v2, prefix=v2_url + "/warehouses")


def main():
    app_port = int(os.getenv("TEST_PORT", 8000))
    uvicorn.run(app, port=app_port)


if __name__ == "__main__":
    main()
