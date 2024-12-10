from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.shipment import Shipment
from typing import Dict, Union
from utils.globals import pagination_url

shipment_router_v2 = APIRouter(tags=["v2.Shipments"])


@shipment_router_v2.get("/{shipment_id}")
def read_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    return shipment


@shipment_router_v2.get("/")
@shipment_router_v2.get(pagination_url)
def read_shipments(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    shipments = data_provider_v2.fetch_shipment_pool().get_shipments()
    if shipments is None:
        raise HTTPException(status_code=404, detail="No shipments found")
    return pagination.apply(shipments)


@shipment_router_v2.get("/{shipment_id}/orders")
@shipment_router_v2.get("/{shipment_id}/orders" + pagination_url)
def read_orders_for_shipment(
    shipment_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    orders = data_provider_v2.fetch_order_pool().get_orders_for_shipments(shipment_id)
    return pagination.apply(orders)


@shipment_router_v2.get("/{shipment_id}/items")
@shipment_router_v2.get("/{shipment_id}/items" + pagination_url)
def read_items_for_shipment(
    shipment_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    items = data_provider_v2.fetch_shipment_pool().get_items_in_shipment(shipment_id)
    return pagination.apply(items)


@shipment_router_v2.post("/")
def create_shipment(
    shipment: Shipment, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    created_shipment = data_provider_v2.fetch_shipment_pool().add_shipment(shipment)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_shipment.model_dump()
    )


@shipment_router_v2.put("/{shipment_id}")
def update_shipment(
    shipment_id: int,
    shipment: Shipment,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingShipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if existingShipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    updated_shipment = data_provider_v2.fetch_shipment_pool().update_shipment(
        shipment_id, shipment
    )
    return updated_shipment


@shipment_router_v2.put("/{shipment_id}/orders")
def update_orders_in_shipment(
    shipment_id: int,
    updated_orders: Dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    updated_order_in_shipment = (
        data_provider_v2.fetch_order_pool().update_orders_in_shipment(
            shipment_id, updated_orders
        )
    )
    return updated_order_in_shipment


@shipment_router_v2.put("/{shipment_id}/items")
def update_items_in_shipment(
    shipment_id: int,
    updated_item: Dict[str, Union[str, int]],
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    updated_item_in_shipment = (
        data_provider_v2.fetch_shipment_pool().update_items_in_shipment(
            shipment_id, [updated_item]
        )
    )
    return updated_item_in_shipment


@shipment_router_v2.put("/{shipment_id}/commit")
def commit_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    return shipment


@shipment_router_v2.patch("/{shipment_id}")
def partial_update_shipment(
    shipment_id: int,
    shipment: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)
    if existing_shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    valid_keys = Shipment.model_fields.keys()
    update_data = {key: value for key, value in shipment.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_shipment, key, value)

    partial_updated_shipment = data_provider_v2.fetch_shipment_pool().update_shipment(
        shipment_id, existing_shipment
    )
    return partial_updated_shipment


@shipment_router_v2.delete("/{shipment_id}")
def delete_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    shipment_pool = data_provider_v2.fetch_shipment_pool()
    shipment = shipment_pool.get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment_pool.remove_shipment(shipment_id)
    return {"massage": "Shipment deleted successfully"}
