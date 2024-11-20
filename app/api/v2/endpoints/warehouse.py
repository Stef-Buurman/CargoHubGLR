from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider_v2
from models.v2.warehouse import Warehouse

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
def read_warehouses(api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    warehouses = data_provider_v2.fetch_warehouse_pool().get_warehouses()
    if warehouses is None:
        raise HTTPException(status_code=404, detail="No warehouses found")
    return warehouses


@warehouse_router_v2.get("/{warehouse_id}/locations")
def read_locations_in_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
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
    # if locations is None:
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
    return locations


@warehouse_router_v2.post("/")
def create_warehouse(
    warehouse: Warehouse, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existing_warehouse = data_provider_v2.fetch_warehouse_pool().get_warehouse(
        warehouse.id
    )
    if existing_warehouse is not None:
        raise HTTPException(status_code=409, detail="Warehouse already exists")
    created_warehouse = data_provider_v2.fetch_warehouse_pool().add_warehouse(warehouse)
    data_provider_v2.fetch_warehouse_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_warehouse.model_dump()
    )


@warehouse_router_v2.put("/{warehouse_id}")
def update_warehouse(
    warehouse_id: int,
    warehouse: Warehouse,
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
    data_provider_v2.fetch_warehouse_pool().save()
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

    for key, value in warehouse.items():
        setattr(existing_warehouse, key, value)

    partial_updated_warehouse = (
        data_provider_v2.fetch_warehouse_pool().update_warehouse(
            warehouse_id, existing_warehouse
        )
    )
    data_provider_v2.fetch_warehouse_pool().save()
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
    data_provider_v2.fetch_warehouse_pool().save()
    return {"message": "Warehouse deleted successfully"}
