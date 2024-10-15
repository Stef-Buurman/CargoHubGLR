from fastapi import APIRouter, Depends
from api.providers import data_provider, auth_provider
from api.providers import auth_provider
from api.providers import data_provider

item_router = APIRouter()

@item_router.get("/items/{item_id}")
def read_item(item_id: str, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_item(item_id)
    return items

@item_router.get("/items")
def read_items(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_items()
    return items

