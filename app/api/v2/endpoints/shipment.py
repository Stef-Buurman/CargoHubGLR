from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.v2.order import Order
from models.v2.ItemInObject import ItemInObject
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.shipment import Shipment
from typing import Dict, List
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
    is_archived = data_provider_v2.fetch_shipment_pool().is_shipment_archived(
        shipment_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Shipment is archived")
    updated_shipment = data_provider_v2.fetch_shipment_pool().update_shipment(
        shipment_id, shipment
    )
    return updated_shipment


@shipment_router_v2.put("/{shipment_id}/orders")
def update_orders_in_shipment(
    shipment_id: int,
    updated_orders: List[Order],
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_shipment_pool().is_shipment_archived(
        shipment_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Shipment is archived")
    updated_order_in_shipment = (
        data_provider_v2.fetch_order_pool().update_orders_in_shipment(
            shipment_id, updated_orders
        )
    )
    return updated_order_in_shipment


@shipment_router_v2.put("/{shipment_id}/items")
def update_items_in_shipment(
    shipment_id: int,
    updated_item: List[ItemInObject],
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_shipment_pool().is_shipment_archived(
        shipment_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Shipment is archived")
    updated_item_in_shipment = (
        data_provider_v2.fetch_shipment_pool().update_items_in_shipment(
            shipment_id, updated_item
        )
    )
    return updated_item_in_shipment


@shipment_router_v2.put("/{shipment_id}/commit")
def commit_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_shipment_pool().is_shipment_archived(
        shipment_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Shipment with id {shipment_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Shipment is archived")

    committed_shipment = data_provider_v2.fetch_shipment_pool().commit_shipment(
        shipment_id
    )
    if committed_shipment is None:
        raise HTTPException(
            status_code=400, detail=f"Shipment is already delivered"
        )
    return committed_shipment


@shipment_router_v2.patch("/{shipment_id}")
def partial_update_shipment(
    shipment_id: int,
    shipment: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_shipment_pool().is_shipment_archived(
        shipment_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Shipment is archived")

    existing_shipment = data_provider_v2.fetch_shipment_pool().get_shipment(shipment_id)

    valid_keys = Shipment.model_fields.keys()
    update_data = {key: value for key, value in shipment.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_shipment, key, value)

    partial_updated_shipment = data_provider_v2.fetch_shipment_pool().update_shipment(
        shipment_id, existing_shipment
    )
    return partial_updated_shipment


@shipment_router_v2.patch("/{shipment_id}/unarchive")
def unarchive_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    shipment_pool = data_provider_v2.fetch_shipment_pool()
    is_archived = shipment_pool.is_shipment_archived(shipment_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="Shipment is not archived")
    updated_shipment = shipment_pool.unarchive_shipment(shipment_id)
    return updated_shipment


@shipment_router_v2.delete("/{shipment_id}")
def archive_shipment(
    shipment_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    shipment_pool = data_provider_v2.fetch_shipment_pool()
    is_archived = shipment_pool.is_shipment_archived(shipment_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Shipment is already archived")
    updated_shipment = shipment_pool.archive_shipment(shipment_id)
    return updated_shipment
