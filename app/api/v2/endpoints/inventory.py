from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.v2.inventory import Inventory
from services import data_provider_v2, auth_provider_v2

inventory_router_v2 = APIRouter()


@inventory_router_v2.get("/{inventory_id}")
def read_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
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
def read_inventories(api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    inventories = data_provider_v2.fetch_inventory_pool().get_inventories()
    if inventories is None:
        raise HTTPException(status_code=404, detail="inventories not found")
    return inventories


@inventory_router_v2.post("/")
def create_inventory(
    inventory: Inventory, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existingInventory = data_provider_v2.fetch_inventory_pool().get_inventory(
        inventory.id
    )
    if existingInventory is not None:
        raise HTTPException(status_code=409, detail="inventory already exists")
    created_inventory = data_provider_v2.fetch_inventory_pool().add_inventory(inventory)
    data_provider_v2.fetch_inventory_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_inventory.model_dump()
    )


@inventory_router_v2.put("/{inventory_id}")
def update_inventory(
    inventory_id: int,
    inventory: Inventory,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    inventory_exists = data_provider_v2.fetch_inventory_pool().get_inventory(
        inventory_id
    )
    if inventory_exists is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    updated_inventory = data_provider_v2.fetch_inventory_pool().update_inventory(
        inventory_id, inventory
    )
    data_provider_v2.fetch_inventory_pool().save()
    return updated_inventory


@inventory_router_v2.patch("/{inventory_id}")
def partial_update_inventory(
    inventory_id: int,
    inventory: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_inventory = data_provider_v2.fetch_inventory_pool().get_inventory(
        inventory_id
    )
    if existing_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")

    valid_keys = Inventory.model_fields.keys()
    update_data = {key: value for key, value in inventory.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_inventory, key, value)

    partial_updated_inventory = (
        data_provider_v2.fetch_inventory_pool().update_inventory(
            inventory_id, existing_inventory
        )
    )
    data_provider_v2.fetch_inventory_pool().save()
    return partial_updated_inventory


@inventory_router_v2.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    inventory_pool = data_provider_v2.fetch_inventory_pool()

    inventory = inventory_pool.get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")

    inventory_pool.remove_inventory(inventory_id)
    inventory_pool.save()
    return {"message": "inventory deleted successfully"}
