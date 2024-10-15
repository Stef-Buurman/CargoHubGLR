from fastapi import APIRouter, Depends, HTTPException, Security
from api.providers import data_provider, auth_provider
from fastapi.security.api_key import APIKeyHeader


warehouse_router = APIRouter()


@warehouse_router.get("/{warehouse_id}")
def read_warehouse(warehouse_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().get_warehouse(warehouse_id)
    return warehouse


@warehouse_router.get("/")
def read_warehouses(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    warehouses = data_provider.fetch_warehouse_pool().get_warehouses()
    return warehouses


@warehouse_router.post("/")
def create_warehouse(warehouse: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    data_provider.fetch_warehouse_pool().add_warehouse(warehouse)
    data_provider.fetch_warehouse_pool().save()
    return warehouse

@warehouse_router.put("/{warehouse_id}")
def update_warehouse(warehouse_id: int, warehouse: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    data_provider.fetch_warehouse_pool().update_warehouse(warehouse_id, warehouse)
    data_provider.fetch_warehouse_pool().save()
    return warehouse

@warehouse_router.delete("/{warehouse_id}")
def delete_warehouse(warehouse_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    data_provider.fetch_warehouse_pool().remove_warehouse(warehouse_id)
    data_provider.fetch_warehouse_pool().save()
    return {"message": "Warehouse deleted successfully"}
