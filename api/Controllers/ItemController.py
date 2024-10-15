from fastapi import APIRouter, Depends, HTTPException
from providers import data_provider, auth_provider

item_router = APIRouter()

@item_router.get("/{item_id}")
def read_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_item(item_id)
    if items is None:
        raise HTTPException(status_code=404, detail="Item with id " + item_id + " not found")
    return items

@item_router.get("/")
def read_items(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_items()
    return items

@item_router.post("/")
def create_item(item: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    data_provider.fetch_item_pool().add_item(item)
    data_provider.fetch_item_pool().save()
    return item

@item_router.put("/{item_id}")
def update_item(item_id: str, item: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    data_provider.fetch_item_pool().update_item(item_id, item)
    data_provider.fetch_item_pool().save()
    return item

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
