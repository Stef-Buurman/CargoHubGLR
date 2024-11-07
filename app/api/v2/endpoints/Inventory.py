from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.v2.inventory import Inventory
from services import data_provider_v2, auth_provider

inventory_router_v2 = APIRouter()


@inventory_router_v2.get("/{inventory_id}")
def read_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    inventory = data_provider_v2.fetch_inventory_pool().get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(
            status_code=404,
            detail="inventory with id " + str(inventory_id) + " not found",
        )
    return inventory


@inventory_router_v2.get("/")
def read_inventories(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    inventories = data_provider_v2.fetch_inventory_pool().get_inventories()
    if inventories is None:
        raise HTTPException(status_code=404, detail="inventories not found")
    return inventories


@inventory_router_v2.post("/")
def create_inventory(
    inventorie: Inventory, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    existingInventorie = data_provider_v2.fetch_inventory_pool().get_inventory(
        inventorie.id
    )
    if existingInventorie is not None:
        raise HTTPException(status_code=409, detail="inventory already exists")
    data_provider_v2.fetch_inventory_pool().add_inventory(inventorie)
    data_provider_v2.fetch_inventory_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=inventorie.model_dump()
    )


@inventory_router_v2.put("/{inventory_id}")
def update_inventory(
    inventory_id: int,
    inventorie: Inventory,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider_v2.init()
    inventory = data_provider_v2.fetch_inventory_pool().get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    data_provider_v2.fetch_inventory_pool().update_inventory(inventory_id, inventorie)
    data_provider_v2.fetch_inventory_pool().save()
    return inventorie


@inventory_router_v2.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    inventory_pool = data_provider_v2.fetch_inventory_pool()

    inventory = inventory_pool.get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")

    inventory_pool.remove_inventory(inventory_id)
    inventory_pool.save()
    return {"message": "inventory deleted successfully"}