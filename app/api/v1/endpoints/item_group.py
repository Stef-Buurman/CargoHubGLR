from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

item_group_router = APIRouter(tags=["v1.Item Groups"], prefix="/item_groups")


@item_group_router.get("/{item_group_id}")
def read_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_group = data_provider.fetch_item_group_pool().get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(
            status_code=404, detail=f"Item_group with id {item_group_id} not found"
        )
    return item_group


@item_group_router.get("/")
def read_item_groups(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    item_groups = data_provider.fetch_item_group_pool().get_item_groups()
    if item_groups is None:
        raise HTTPException(status_code=404, detail="No item_groups found")
    return item_groups


@item_group_router.get("/{item_group_id}/items")
def read_items_for_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_group = data_provider.fetch_item_group_pool().get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(
            status_code=404, detail=f"Item_group with id {item_group_id} not found"
        )
    items = data_provider.fetch_item_pool().get_items_for_item_group(item_group_id)
    return items


@item_group_router.post("/")
def create_item_group(
    item_group: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingitem_group = data_provider.fetch_item_group_pool().get_item_group(
        item_group["id"]
    )
    if existingitem_group is not None:
        raise HTTPException(status_code=409, detail="Item_group already exists")
    data_provider.fetch_item_group_pool().add_item_group(item_group)
    data_provider.fetch_item_group_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item_group)


@item_group_router.put("/{item_group_id}")
def update_item_group(
    item_group_id: int,
    item_group: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider.init()
    existingitem_group = data_provider.fetch_item_group_pool().get_item_group(
        item_group_id
    )
    if existingitem_group is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    data_provider.fetch_item_group_pool().update_item_group(item_group_id, item_group)
    data_provider.fetch_item_group_pool().save()
    return item_group


@item_group_router.delete("/{item_group_id}")
def delete_item_group(
    item_group_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_group_pool = data_provider.fetch_item_group_pool()
    item_group = item_group_pool.get_item_group(item_group_id)
    if item_group is None:
        raise HTTPException(status_code=404, detail="Item_group not found")
    item_group_pool.remove_item_group(item_group_id)
    item_group_pool.save()
    return {"massage": "Item_group deleted successfully"}
