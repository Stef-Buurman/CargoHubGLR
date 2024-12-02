from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.item import Item
from utils.globals import pagination_url
item_router_v2 = APIRouter()


@item_router_v2.get("/{item_id}")
def read_item(item_id: str, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    items = data_provider_v2.fetch_item_pool().get_item(item_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail="Item with id " + item_id + " not found"
        )
    return items


@item_router_v2.get("/")
@item_router_v2.get(pagination_url)
def read_items(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    items = data_provider_v2.fetch_item_pool().get_items()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return pagination.apply(items)


@item_router_v2.get("/{item_id}/inventory")
@item_router_v2.get("/{item_id}/inventory" + pagination_url)
def read_inventory_of_item(
    item_id: str,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventories = data_provider_v2.fetch_inventory_pool().get_inventories_for_item(
        item_id
    )
    return pagination.apply(inventories)


@item_router_v2.get("/{item_id}/inventory/totals")
def read_inventory_totals_of_item(
    item_id: str, api_key: str = Depends(auth_provider_v2.get_api_key)
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
def create_item(item: Item, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    addedItem = data_provider_v2.fetch_item_pool().add_item(item)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=addedItem.model_dump()
    )


@item_router_v2.put("/{item_id}")
def update_item(
    item_id: str, item: Item, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existingItem = data_provider_v2.fetch_item_pool().get_item(item_id)
    if existingItem is None:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = data_provider_v2.fetch_item_pool().update_item(item_id, item)
    return updated_item


@item_router_v2.patch("/{item_id}")
def partial_update_item(
    item_id: str,
    item: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    valid_keys = Item.model_fields.keys()
    update_data = {key: value for key, value in item.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item, key, value)

    partial_updated_item = data_provider_v2.fetch_item_pool().update_item(
        item_id, existing_item
    )
    return partial_updated_item


@item_router_v2.delete("/{item_id}")
def delete_item(item_id: str, api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    item_pool = data_provider_v2.fetch_item_pool()

    item = item_pool.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_pool.remove_item(item_id)
    return {"message": "Item deleted successfully"}
