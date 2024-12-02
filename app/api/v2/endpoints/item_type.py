from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.item_type import ItemType
from utils.globals import pagination_url
item_type_router_v2 = APIRouter()


@item_type_router_v2.get("/{item_type_id}")
def read_item_type(
    item_type_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_type = data_provider_v2.fetch_item_type_pool().get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(
            status_code=404, detail=f"Item_type with id {item_type_id} not found"
        )
    return item_type


@item_type_router_v2.get("/")
@item_type_router_v2.get(pagination_url)
def read_item_types(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    item_types = data_provider_v2.fetch_item_type_pool().get_item_types()
    if item_types is None:
        raise HTTPException(status_code=404, detail="No item_types found")
    return pagination.apply(item_types)


@item_type_router_v2.get("/{item_type_id}/items")
@item_type_router_v2.get("/{item_type_id}/items" + pagination_url)
def read_items_for_item_type(
    item_type_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    item_type = data_provider_v2.fetch_item_type_pool().get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(
            status_code=404, detail=f"Item_type with id {item_type_id} not found"
        )
    items = data_provider_v2.fetch_item_pool().get_items_for_item_type(item_type_id)
    return pagination.apply(items)


@item_type_router_v2.post("/")
def create_item_type(
    item_type: ItemType, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    added_item_type = data_provider_v2.fetch_item_type_pool().add_item_type(item_type)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=added_item_type.model_dump()
    )


@item_type_router_v2.put("/{item_type_id}")
def update_item_type(
    item_type_id: int,
    item_type: ItemType,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingitem_type = data_provider_v2.fetch_item_type_pool().get_item_type(
        item_type_id
    )
    if existingitem_type is None:
        raise HTTPException(status_code=404, detail="Item_type not found")
    updated_item_type = data_provider_v2.fetch_item_type_pool().update_item_type(
        item_type_id, item_type
    )
    return updated_item_type


@item_type_router_v2.patch("/{item_type_id}")
def partial_update_item_type(
    item_type_id: int,
    item_type: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_item_type = data_provider_v2.fetch_item_type_pool().get_item_type(
        item_type_id
    )
    if existing_item_type is None:
        raise HTTPException(status_code=404, detail="item_type not found")

    valid_keys = ItemType.model_fields.keys()
    update_data = {key: value for key, value in item_type.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item_type, key, value)

    partial_updated_item_type = (
        data_provider_v2.fetch_item_type_pool().update_item_type(
            item_type_id, existing_item_type
        )
    )
    return partial_updated_item_type


@item_type_router_v2.delete("/{item_type_id}")
def delete_item_type(
    item_type_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_type_pool = data_provider_v2.fetch_item_type_pool()
    item_type = item_type_pool.get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(status_code=404, detail="Item_type not found")
    if not item_type_pool.remove_item_type(item_type_id):
        raise HTTPException(
            status_code=409,
            detail="Item_type is in use and cannot be deleted",
        )
    return {"message": "Item_type deleted successfully"}
