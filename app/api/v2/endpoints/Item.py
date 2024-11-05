from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider
from models.v2.item import Item

item_router_v2 = APIRouter()


@item_router_v2.get("/{item_id}")
def read_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    items = data_provider_v2.fetch_item_pool().get_item(item_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail="Item with id " + item_id + " not found"
        )
    return items


@item_router_v2.get("/")
def read_items(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    items = data_provider_v2.fetch_item_pool().get_items()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@item_router_v2.get("/{item_id}/inventory")
def read_inventory_of_item(
    item_id: str, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventories = data_provider_v2.fetch_inventory_pool().get_inventories_for_item(
        item_id
    )
    return inventories


@item_router_v2.get("/{item_id}/inventory/totals")
def read_inventory_totals_of_item(
    item_id: str, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory_totals = (
        data_provider_v2.fetch_inventory_pool().get_inventory_totals_for_item(item_id)
    )
    return inventory_totals


@item_router_v2.post("/")
def create_item(item: Item, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    data_provider_v2.fetch_item_pool().add_item(item)
    data_provider_v2.fetch_item_pool().save()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item.dict())


@item_router_v2.put("/{item_id}")
def update_item(
    item_id: str, item: Item, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    existingItem = data_provider_v2.fetch_item_pool().get_item(item_id)
    if existingItem is None:
        raise HTTPException(status_code=404, detail="Item not found")
    data_provider_v2.fetch_item_pool().update_item(item_id, item)
    data_provider_v2.fetch_item_pool().save()
    return item


@item_router_v2.delete("/{item_id}")
def delete_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    item_pool = data_provider_v2.fetch_item_pool()

    item = item_pool.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_pool.remove_item(item_id)
    item_pool.save()
    return {"message": "Item deleted successfully"}
