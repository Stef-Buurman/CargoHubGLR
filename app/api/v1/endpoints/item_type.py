from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

item_type_router = APIRouter(tags=["v1.Item Types"], prefix="/item_types")


@item_type_router.get("/{item_type_id}")
def read_item_type(
    item_type_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_type = data_provider.fetch_item_type_pool().get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(
            status_code=404, detail=f"Item_type with id {item_type_id} not found"
        )
    return item_type


@item_type_router.get("")
def read_item_types(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    item_types = data_provider.fetch_item_type_pool().get_item_types()
    if item_types is None:
        raise HTTPException(status_code=404, detail="No item_types found")
    return item_types


@item_type_router.get("/{item_type_id}/items")
def read_items_for_item_type(
    item_type_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_type = data_provider.fetch_item_type_pool().get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(
            status_code=404, detail=f"Item_type with id {item_type_id} not found"
        )
    items = data_provider.fetch_item_pool().get_items_for_item_type(item_type_id)
    return items


@item_type_router.post("")
def create_item_type(
    item_type: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingitem_type = data_provider.fetch_item_type_pool().get_item_type(
        item_type.get("id")
    )
    if existingitem_type is not None:
        raise HTTPException(status_code=409, detail="Item_type already exists")
    created_item_type =  data_provider.fetch_item_type_pool().add_item_type(item_type)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item_type)


@item_type_router.put("/{item_type_id}")
def update_item_type(
    item_type_id: int,
    item_type: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider.init()
    existingitem_type = data_provider.fetch_item_type_pool().get_item_type(item_type_id)
    if existingitem_type is None:
        raise HTTPException(status_code=404, detail="Item_type not found")
    data_provider.fetch_item_type_pool().update_item_type(item_type_id, item_type)
    data_provider.fetch_item_type_pool().save()
    return item_type


@item_type_router.delete("/{item_type_id}")
def delete_item_type(
    item_type_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_type_pool = data_provider.fetch_item_type_pool()
    item_type = item_type_pool.get_item_type(item_type_id)
    if item_type is None:
        raise HTTPException(status_code=404, detail="Item_type not found")
    item_type_pool.remove_item_type(item_type_id)
    item_type_pool.save()
    return {"message": "Item_type deleted successfully"}
