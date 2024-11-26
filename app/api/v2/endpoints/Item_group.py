from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from models.v2.item_group import ItemGroup
from services import data_provider_v2, auth_provider_v2

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
def read_item_groups(api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    item_groups = data_provider_v2.fetch_item_group_pool().get_item_groups()
    if item_groups is None:
        raise HTTPException(status_code=404, detail="No item_groups found")
    return item_groups


@item_group_router_v2.get("/{item_group_id}/items")
def read_items_for_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_group = data_provider_v2.fetch_item_group_pool().get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(
            status_code=404, detail=f"Item_group with id {item_group_id} not found"
        )
    items = data_provider_v2.fetch_item_pool().get_items_for_item_group(item_group_id)
    # if not items:
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
    return items


@item_group_router_v2.post("/")
def create_item_group(
    item_group: ItemGroup, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existingitem_group = data_provider_v2.fetch_item_group_pool().get_item_group(
        item_group.id
    )
    if existingitem_group is not None:
        raise HTTPException(status_code=409, detail="Item_group already exists")
    added_item_group = data_provider_v2.fetch_item_group_pool().add_item_group(
        item_group
    )
    data_provider_v2.fetch_item_group_pool().save()
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
    data_provider_v2.fetch_item_group_pool().save()
    return updated_item_group


@item_group_router_v2.patch("/{item_group_id}")
def partial_update_item_group(
    item_group_id: int,
    item_group: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_item_group = data_provider_v2.fetch_item_group_pool().get_item_group(
        item_group_id
    )
    if existing_item_group is None:
        raise HTTPException(status_code=404, detail="Item_group not found")

    valid_keys = ItemGroup.model_fields.keys()
    update_data = {key: value for key, value in item_group.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item_group, key, value)

    partial_updated_item_group = (
        data_provider_v2.fetch_item_group_pool().update_item_group(
            item_group_id, existing_item_group
        )
    )
    data_provider_v2.fetch_item_group_pool().save()
    return partial_updated_item_group


@item_group_router_v2.delete("/{item_group_id}")
def delete_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_group_pool = data_provider_v2.fetch_item_group_pool()
    item_group = item_group_pool.get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    item_group_pool.remove_item_group(item_group_id)
    item_group_pool.save()
    return {"massage": "Item_group deleted successfully"}
