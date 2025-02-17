from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2 import data_provider_v2
from models.v2.item import Item

item_router_v2 = APIRouter(tags=["v2.Items"], prefix="/items")


@item_router_v2.get("/{item_id}")
def read_item(item_id: str):
    items = data_provider_v2.fetch_item_pool().get_item(item_id)
    if items is None:
        raise HTTPException(
            status_code=404, detail="Item with id " + item_id + " not found"
        )
    return items


@item_router_v2.get("")
def read_items(request: Request):
    items = data_provider_v2.fetch_item_pool().get_items()
    if items is None:
        raise HTTPException(status_code=404, detail="Items not found")
    return request.state.pagination.apply(items)


@item_router_v2.get("/{item_id}/inventory")
def read_inventory_of_item(item_id: str, request: Request):
    item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventories = data_provider_v2.fetch_inventory_pool().get_inventories_for_item(
        item_id
    )
    return request.state.pagination.apply(inventories)


@item_router_v2.get("/{item_id}/inventory/totals")
def read_inventory_totals_of_item(item_id: str):
    item = data_provider_v2.fetch_item_pool().get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory_totals = (
        data_provider_v2.fetch_inventory_pool().get_inventory_totals_for_item(item_id)
    )
    return inventory_totals


@item_router_v2.post("")
def create_item(item: Item):
    addedItem = data_provider_v2.fetch_item_pool().add_item(item)
    if addedItem is None:
        raise HTTPException(
            status_code=400,
            detail="Item cannot be created, maybe due to archived entities",
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=addedItem.model_dump()
    )


@item_router_v2.put("/{item_id}")
def update_item(item_id: str, item: Item):
    existing_item = data_provider_v2.fetch_item_pool().is_item_archived(item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    elif existing_item is True:
        raise HTTPException(status_code=400, detail="Item is archived")
    updated_item = data_provider_v2.fetch_item_pool().update_item(item_id, item)
    return updated_item


@item_router_v2.patch("/{item_id}")
def partial_update_item(item_id: str, item: dict):
    is_archived = data_provider_v2.fetch_item_pool().is_item_archived(item_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Item is archived")
    existing_item = data_provider_v2.fetch_item_pool().get_item(item_id)

    valid_keys = Item.model_fields.keys()
    update_data = {key: value for key, value in item.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item, key, value)

    partial_updated_item = data_provider_v2.fetch_item_pool().update_item(
        item_id, existing_item
    )
    return partial_updated_item


@item_router_v2.patch("/{item_id}/unarchive")
def unarchive_item(item_id: str):
    item_pool = data_provider_v2.fetch_item_pool()

    is_archived = item_pool.is_item_archived(item_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="Item is not archived")

    updated_item = item_pool.unarchive_item(item_id)
    return updated_item


@item_router_v2.delete("/{item_id}")
def archive_item(item_id: str):
    item_pool = data_provider_v2.fetch_item_pool()

    is_archived = item_pool.is_item_archived(item_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Item is already archived")

    updated_item = item_pool.archive_item(item_id)
    return updated_item
