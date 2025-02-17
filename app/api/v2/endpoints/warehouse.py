from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from services.v2 import data_provider_v2
from models.v2.warehouse import Warehouse

warehouse_router_v2 = APIRouter(tags=["v2.Warehouses"], prefix="/warehouses")


@warehouse_router_v2.get("/{warehouse_id}")
def read_warehouse(warehouse_id: int):
    warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@warehouse_router_v2.get("")
def read_warehouses(request: Request):
    warehouses = data_provider_v2.fetch_warehouse_pool().get_warehouses()
    if warehouses is None:
        raise HTTPException(status_code=404, detail="No warehouses found")
    return request.state.pagination.apply(warehouses)


@warehouse_router_v2.get("/{warehouse_id}/locations")
def read_locations_in_warehouse(warehouse_id: int, request: Request):
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
    return request.state.pagination.apply(locations)


@warehouse_router_v2.post("")
def create_warehouse(warehouse: Warehouse):
    created_warehouse = data_provider_v2.fetch_warehouse_pool().add_warehouse(warehouse)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_warehouse.model_dump()
    )


@warehouse_router_v2.put("/{warehouse_id}")
def update_warehouse(warehouse_id: int, warehouse: Warehouse):
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
        warehouse_id
    )
    if existing_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    elif existing_warehouse:
        raise HTTPException(status_code=400, detail="Warehouse is archived")
    updated_warehouse = data_provider_v2.fetch_warehouse_pool().update_warehouse(
        warehouse_id, warehouse
    )
    return updated_warehouse


@warehouse_router_v2.patch("/{warehouse_id}")
def partial_update_warehouse(warehouse_id: int, warehouse: dict):
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
        warehouse_id
    )
    if existing_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    elif existing_warehouse:
        raise HTTPException(status_code=400, detail="Warehouse is archived")
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(
        warehouse_id
    )

    valid_keys = Warehouse.model_fields.keys()
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
def archive_warehouse(warehouse_id: int):
    warehouse = data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
        warehouse_id
    )
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    elif warehouse:
        raise HTTPException(status_code=400, detail="Warehouse already archived")

    updated_warehouse = data_provider_v2.fetch_warehouse_pool().archive_warehouse(
        warehouse_id
    )
    return updated_warehouse


@warehouse_router_v2.patch("/{warehouse_id}/unarchive")
def unarchive_warehouse(warehouse_id: int):
    warehouse = data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
        warehouse_id
    )
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    elif not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse already unarchived")

    updated_warehouse = data_provider_v2.fetch_warehouse_pool().unarchive_warehouse(
        warehouse_id
    )
    return updated_warehouse
