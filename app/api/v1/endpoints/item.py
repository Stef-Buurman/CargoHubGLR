from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

item_router = APIRouter(tags=["v1.Items"], prefix="/items")


@item_router.get("/{item_id}")
def read_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_item(item_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail="Item with id " + item_id + " not found"
        )
    return items


@item_router.get("")
def read_items(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_items()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@item_router.get("/{item_id}/inventory")
def read_inventory_of_item(
    item_id: str, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item = data_provider.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventories = data_provider.fetch_inventory_pool().get_inventories_for_item(item_id)
    return inventories


@item_router.get("/{item_id}/inventory/totals")
def read_inventory_totals_of_item(
    item_id: str, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item = data_provider.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory_totals = (
        data_provider.fetch_inventory_pool().get_inventory_totals_for_item(item_id)
    )
    return inventory_totals


@item_router.post("")
def create_item(item: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existingItem = data_provider.fetch_item_pool().get_item(item.get("uid"))
    if existingItem is not None:
        raise HTTPException(status_code=409, detail="Item already exists")
    created_item = data_provider.fetch_item_pool().add_item(item)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)


@item_router.put("/{item_id}")
def update_item(
    item_id: str, item: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingItem = data_provider.fetch_item_pool().get_item(item_id)
    if existingItem is None:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = data_provider.fetch_item_pool().update_item(item_id, item)
    return updated_item


@item_router.delete("/{item_id}")
def delete_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    item_pool = data_provider.fetch_item_pool()

    item = item_pool.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_pool.remove_item(item_id)
    item_pool.save()
    return {"message": "Item deleted successfully"}
