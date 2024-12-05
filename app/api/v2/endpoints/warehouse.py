from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.warehouse import WarehouseDB
from utils.globals import pagination_url

warehouse_router_v2 = APIRouter()


@warehouse_router_v2.get("/{warehouse_id}")
def read_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@warehouse_router_v2.get("/")
@warehouse_router_v2.get(pagination_url)
def read_warehouses(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    warehouses = data_provider_v2.fetch_warehouse_pool().get_warehouses()
    if warehouses is None:
        raise HTTPException(status_code=404, detail="No warehouses found")
    return pagination.apply(warehouses)


@warehouse_router_v2.get("/{warehouse_id}/locations")
@warehouse_router_v2.get("/{warehouse_id}/locations" + pagination_url)
def read_locations_in_warehouse(
    warehouse_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(
            status_code=404, detail=f"Warehouse with id {warehouse_id} not found"
        )
    locations = data_provider_v2.fetch_location_pool().get_locations_in_warehouse(
        warehouse_id
    )
    if locations is None:
        raise HTTPException(
            status_code=404, detail=f"No locations found in warehouse {warehouse_id}"
        )
    return pagination.apply(locations)


@warehouse_router_v2.post("/")
def create_warehouse(
    warehouse: WarehouseDB, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    created_warehouse = data_provider_v2.fetch_warehouse_pool().add_warehouse(warehouse)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_warehouse.model_dump()
    )


@warehouse_router_v2.put("/{warehouse_id}")
def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseDB,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(
        warehouse_id
    )
    if existing_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    updated_warehouse = data_provider_v2.fetch_warehouse_pool().update_warehouse(
        warehouse_id, warehouse
    )
    return updated_warehouse


@warehouse_router_v2.patch("/{warehouse_id}")
def partial_update_warehouse(
    warehouse_id: int,
    warehouse: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(
        warehouse_id
    )
    if existing_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    valid_keys = WarehouseDB.model_fields.keys()
    update_data = {key: value for key, value in warehouse.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_warehouse, key, value)

    partial_updated_warehouse = (
        data_provider_v2.fetch_warehouse_pool().update_warehouse(
            warehouse_id, existing_warehouse
        )
    )
    return partial_updated_warehouse


@warehouse_router_v2.delete("/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    data_provider_v2.fetch_warehouse_pool().remove_warehouse(warehouse_id)
    return {"message": "Warehouse deleted successfully"}
