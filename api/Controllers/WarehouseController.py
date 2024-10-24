from fastapi import APIRouter, Depends, HTTPException, status, Response
from providers import data_provider, auth_provider
from fastapi.responses import JSONResponse


warehouse_router = APIRouter()


@warehouse_router.get("/{warehouse_id}")
def read_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@warehouse_router.get("/")
def read_warehouses(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    warehouses = data_provider.fetch_warehouse_pool().get_warehouses()
    if warehouses is None:
        raise HTTPException(status_code=404, detail="No warehouses found")
    return warehouses


@warehouse_router.get("/{warehouse_id}/locations")
def read_locations_in_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(
            status_code=404, detail=f"Warehouse with id {warehouse_id} not found"
        )
    locations = data_provider.fetch_location_pool().get_locations_in_warehouse(
        warehouse_id
    )
    # if locations is None:
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
    return locations


@warehouse_router.post("/")
def create_warehouse(
    warehouse: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existing_warehouse = data_provider.fetch_warehouse_pool().get_warehouse(
        warehouse["id"]
    )
    if existing_warehouse is not None:
        raise HTTPException(status_code=409, detail="Warehouse already exists")
    data_provider.fetch_warehouse_pool().add_warehouse(warehouse)
    data_provider.fetch_warehouse_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=warehouse)


@warehouse_router.put("/{warehouse_id}")
def update_warehouse(
    warehouse_id: int,
    warehouse: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider.init()
    existing_warehouse = data_provider.fetch_warehouse_pool().get_warehouse(
        warehouse_id
    )
    if existing_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    data_provider.fetch_warehouse_pool().update_warehouse(warehouse_id, warehouse)
    data_provider.fetch_warehouse_pool().save()
    return warehouse


@warehouse_router.delete("/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    warehouse = data_provider.fetch_warehouse_pool().get_warehouse(warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    data_provider.fetch_warehouse_pool().remove_warehouse(warehouse_id)
    data_provider.fetch_warehouse_pool().save()
    return {"message": "Warehouse deleted successfully"}
