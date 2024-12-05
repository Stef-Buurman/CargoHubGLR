from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from models.v2.item_group import ItemGroup
from services.v2 import data_provider_v2, auth_provider_v2
from utils.globals import pagination_url

item_group_router_v2 = APIRouter()


@item_group_router_v2.get("/{item_group_id}")
def read_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_group = data_provider_v2.fetch_item_group_pool().get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(
            status_code=404, detail=f"Item_group with id {item_group_id} not found"
        )
    return item_group


@item_group_router_v2.get("/")
@item_group_router_v2.get(pagination_url)
def read_item_groups(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    item_groups = data_provider_v2.fetch_item_group_pool().get_item_groups()
    if item_groups is None:
        raise HTTPException(status_code=404, detail="No item_groups found")
    return pagination.apply(item_groups)


@item_group_router_v2.get("/{item_group_id}/items")
@item_group_router_v2.get("/{item_group_id}/items" + pagination_url)
def read_items_for_item_group(
    item_group_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    item_group = data_provider_v2.fetch_item_group_pool().get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(
            status_code=404, detail=f"Item_group with id {item_group_id} not found"
        )
    items = data_provider_v2.fetch_item_pool().get_items_for_item_group(item_group_id)
    return pagination.apply(items)


@item_group_router_v2.post("/")
def create_item_group(
    item_group: ItemGroup, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    added_item_group = data_provider_v2.fetch_item_group_pool().add_item_group(
        item_group
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=added_item_group.model_dump()
    )


@item_group_router_v2.put("/{item_group_id}")
def update_item_group(
    item_group_id: int,
    item_group: ItemGroup,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingitem_group = data_provider_v2.fetch_item_group_pool().get_item_group(
        item_group_id
    )
    if existingitem_group is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    updated_item_group = data_provider_v2.fetch_item_group_pool().update_item_group(
        item_group_id, item_group
    )
    return updated_item_group


@item_group_router_v2.patch("/{item_group_id}")
def partial_update_item_group(
    item_group_id: int,
    item_group: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_item_group_pool().is_item_group_archived(
        item_group_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="Item_group is not archived")

    existing_item_group = data_provider_v2.fetch_item_group_pool().get_item_group(
        item_group_id
    )

    valid_keys = ItemGroup.model_fields.keys()
    update_data = {key: value for key, value in item_group.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item_group, key, value)

    partial_updated_item_group = (
        data_provider_v2.fetch_item_group_pool().update_item_group(
            item_group_id, existing_item_group
        )
    )
    return partial_updated_item_group


@item_group_router_v2.patch("/{item_group_id}/unarchive")
def unarchive_item_group(
    item_group_id: int,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    is_archived = data_provider_v2.fetch_item_group_pool().is_item_group_archived(
        item_group_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="Item_group is not archived")

    updated_item_group = data_provider_v2.fetch_item_group_pool().unarchive_item_group(
        item_group_id
    )
    return updated_item_group


@item_group_router_v2.delete("/{item_group_id}")
def archive_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_group_pool = data_provider_v2.fetch_item_group_pool()
    is_archived = item_group_pool.is_item_group_archived(item_group_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Item_group is already archived")

    updated_item_group = item_group_pool.archive_item_group(item_group_id)
    return updated_item_group
