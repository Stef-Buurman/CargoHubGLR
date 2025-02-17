from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

inventory_router = APIRouter(tags=["v1.Inventory"], prefix="/inventories")


@inventory_router.get("/{inventory_id}")
def read_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    inventory = data_provider.fetch_inventory_pool().get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(
            status_code=404,
            detail="inventory with id " + str(inventory_id) + " not found",
        )
    return inventory


@inventory_router.get("")
def read_inventories(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    inventories = data_provider.fetch_inventory_pool().get_inventories()
    if inventories is None:
        raise HTTPException(status_code=404, detail="inventories not found")
    return inventories


@inventory_router.post("")
def create_inventory(
    inventory: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingInventory = data_provider.fetch_inventory_pool().get_inventory(
        inventory.get("id")
    )
    if existingInventory is not None:
        raise HTTPException(status_code=409, detail="inventory already exists")
    created_inventory = data_provider.fetch_inventory_pool().add_inventory(inventory)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_inventory)


@inventory_router.put("/{inventory_id}")
def update_inventory(
    inventory_id: int,
    inventory: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider.init()
    existingInventory = data_provider.fetch_inventory_pool().get_inventory(inventory_id)
    if existingInventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    updated_inventory = data_provider.fetch_inventory_pool().update_inventory(
        inventory_id, inventory
    )
    return updated_inventory


@inventory_router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    inventory_pool = data_provider.fetch_inventory_pool()

    inventory = inventory_pool.get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")

    inventory_pool.remove_inventory(inventory_id)
    inventory_pool.save()
    return {"message": "inventory deleted successfully"}
