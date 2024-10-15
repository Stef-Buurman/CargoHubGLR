from fastapi import APIRouter, Depends, HTTPException, Security
from api.providers import data_provider, auth_provider
from fastapi.security.api_key import APIKeyHeader
from api.providers import auth_provider
from api.providers import data_provider

item_router = APIRouter()

API_KEY_NAME = "api_key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    auth_provider.init()
    if auth_provider.has_access(api_key_header):
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="You dont have access to do this operation"
        )

@item_router.get("/items/{item_id}")
def read_item(item_id: str):
    data_provider.init()
    items = data_provider.fetch_item_pool().get_item(item_id)
    return items

@item_router.get("/items")
def read_items():
    data_provider.init()
    items = data_provider.fetch_item_pool().get_items()
    return items

