from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services import data_provider, auth_provider

order_router = APIRouter()


@order_router.get("/{order_id}")
def read_order(order_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    order = data_provider.fetch_order_pool().get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=404, detail=f"Order with id {order_id} not found"
        )
    return order


@order_router.get("/")
def read_orders(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    orders = data_provider.fetch_order_pool().get_orders()
    if orders is None:
        raise HTTPException(status_code=404, detail="Orders not found")
    return orders


@order_router.get("/{order_id}/items")
def read_order_items(order_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_order_pool().get_items_in_order(order_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail=f"Order with id {order_id} not found"
        )
    return items


@order_router.post("/")
def create_order(order: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existingOrder = data_provider.fetch_order_pool().get_order(order["id"])
    if existingOrder is not None:
        raise HTTPException(status_code=409, detail="Order already exists")
    data_provider.fetch_order_pool().add_order(order)
    data_provider.fetch_order_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=order)


@order_router.put("/{order_id}")
def update_order(
    order_id: int, order: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingOrder = data_provider.fetch_order_pool().get_order(order_id)
    if existingOrder is None:
        raise HTTPException(status_code=404, detail="Order not found")
    data_provider.fetch_order_pool().update_order(order_id, order)
    data_provider.fetch_order_pool().save()
    return order


@order_router.put("/{order_id}/items")
def add_items_to_order(
    order_id: int, items: list[dict], api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingOrder = data_provider.fetch_order_pool().get_order(order_id)
    if existingOrder is None:
        raise HTTPException(status_code=404, detail="Order not found")
    data_provider.fetch_order_pool().update_items_in_order(order_id, items)
    data_provider.fetch_order_pool().save()
    return items


@order_router.delete("/{order_id}")
def delete_order(order_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    order_pool = data_provider.fetch_order_pool()

    order = order_pool.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order_pool.remove_order(order_id)
    order_pool.save()
    return {"message": "Order deleted successfully"}
