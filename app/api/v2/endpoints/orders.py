from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.order import Order
from models.v2.ItemInObject import ItemInObject
from utils.globals import pagination_url

order_router_v2 = APIRouter(tags=["v2.Orders"])


@order_router_v2.get("/{order_id}")
def read_order(order_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    order = data_provider_v2.fetch_order_pool().get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=404, detail=f"Order with id {order_id} not found"
        )
    return order


@order_router_v2.get("/")
@order_router_v2.get(pagination_url)
def read_orders(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    orders = data_provider_v2.fetch_order_pool().get_orders()
    if orders is None:
        raise HTTPException(status_code=404, detail="Orders not found")
    return pagination.apply(orders)


@order_router_v2.get("/{order_id}/items")
@order_router_v2.get("/{order_id}/items" + pagination_url)
def read_order_items(
    order_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    items = data_provider_v2.fetch_order_pool().get_items_in_order(order_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail=f"Order with id {order_id} not found"
        )
    return pagination.apply(items)


@order_router_v2.post("/")
def create_order(order: Order, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    addedOrder = data_provider_v2.fetch_order_pool().add_order(order)
    if addedOrder is None:
        raise HTTPException(status_code=400, detail="Order has archived entities")
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=addedOrder.model_dump()
    )


@order_router_v2.put("/{order_id}")
def update_order(
    order_id: int, order: Order, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existingOrder = data_provider_v2.fetch_order_pool().is_order_archived(order_id)
    if existingOrder is None:
        raise HTTPException(status_code=404, detail="Order not found")
    elif existingOrder:
        raise HTTPException(status_code=400, detail="Order is archived")

    updatedOrder = data_provider_v2.fetch_order_pool().update_order(order_id, order)
    return updatedOrder


@order_router_v2.put("/{order_id}/items")
def add_items_to_order(
    order_id: int,
    items: list[ItemInObject],
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingOrder = data_provider_v2.fetch_order_pool().is_order_archived(order_id)
    if existingOrder is None:
        raise HTTPException(status_code=404, detail="Order not found")
    elif existingOrder:
        raise HTTPException(status_code=400, detail="Order is archived")

    data_provider_v2.fetch_order_pool().update_items_in_order(order_id, items)
    return items


@order_router_v2.patch("/{order_id}")
def partial_update_order(
    order_id: int,
    order: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_order = data_provider_v2.fetch_order_pool().is_order_archived(order_id)
    if existing_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    elif existing_order:
        raise HTTPException(status_code=400, detail="Order is archived")

    existing_order = data_provider_v2.fetch_order_pool().get_order(order_id)

    valid_keys = Order.model_fields.keys()
    update_data = {key: value for key, value in order.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_order, key, value)

    partial_updated_order = data_provider_v2.fetch_order_pool().update_order(
        order_id, existing_order
    )
    return partial_updated_order


@order_router_v2.delete("/{order_id}")
def archive_order(order_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    order = data_provider_v2.fetch_order_pool().is_order_archived(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    elif order:
        raise HTTPException(status_code=400, detail="Order is already archived")

    data_provider_v2.fetch_order_pool().archive_order(order_id)
    return {"message": "Order archived successfully"}


@order_router_v2.patch("/{order_id}/unarchive")
def unarchive_order(
    order_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    order = data_provider_v2.fetch_order_pool().is_order_archived(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    elif not order:
        raise HTTPException(status_code=400, detail="Order is not archived")

    data_provider_v2.fetch_order_pool().unarchive_order(order_id)
    return {"message": "Order unarchived successfully"}
