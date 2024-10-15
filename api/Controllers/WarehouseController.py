from fastapi import APIRouter, Depends, HTTPException, Security
from api.providers import data_provider, auth_provider
from fastapi.security.api_key import APIKeyHeader
from api.providers import auth_provider
from api.providers import data_provider
from pydantic import BaseModel

warehouse_router = APIRouter()

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


@warehouse_router.get("/warehouse/{warehouse_id}")
def read_warehouse(warehouse_id: int):
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().get_warehouse(warehouse_id)
    return warehouse


@warehouse_router.get("/warehouses")
def read_warehouses():
    data_provider.init()
    warehouses = data_provider.fetch_warehouse_pool().get_warehouses()
    return warehouses


@warehouse_router.post("/warehouse")
def create_warehouse():
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().add_warehouse()
    return warehouse
