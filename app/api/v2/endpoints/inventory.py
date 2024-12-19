from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from models.v2.inventory import Inventory
from services.v2 import data_provider_v2
from utils.globals import pagination_url

inventory_router_v2 = APIRouter(tags=["v2.Inventories"], prefix="/inventories")


@inventory_router_v2.get("/{inventory_id}")
def read_inventory(inventory_id: int):

    inventory = data_provider_v2.fetch_inventory_pool().get_inventory(inventory_id)
    if inventory is None:
        raise HTTPException(
            status_code=404,
            detail="inventory with id " + str(inventory_id) + " not found",
        )
    return inventory


@inventory_router_v2.get("/")
@inventory_router_v2.get(pagination_url)
def read_inventories(pagination: Pagination = Depends()):

    inventories = data_provider_v2.fetch_inventory_pool().get_inventories()
    if not inventories:
        raise HTTPException(status_code=404, detail="No inventories found")
    return pagination.apply(inventories)


@inventory_router_v2.post("/")
def create_inventory(inventory: Inventory):

    created_inventory = data_provider_v2.fetch_inventory_pool().add_inventory(inventory)
    if created_inventory is None:
        raise HTTPException(status_code=400, detail="Inventory has archived entries")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_inventory.model_dump()
    )


@inventory_router_v2.put("/{inventory_id}")
def update_inventory(
    inventory_id: int,
    inventory: Inventory,
):

    is_archived = data_provider_v2.fetch_inventory_pool().is_inventory_archived(
        inventory_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="inventory is archived")
    updated_inventory = data_provider_v2.fetch_inventory_pool().update_inventory(
        inventory_id, inventory
    )

    if updated_inventory is None:
        raise HTTPException(status_code=400, detail="inventory has archived entries")

    return updated_inventory


@inventory_router_v2.patch("/{inventory_id}")
def partial_update_inventory(
    inventory_id: int,
    inventory: dict,
):

    is_archived = data_provider_v2.fetch_inventory_pool().is_inventory_archived(
        inventory_id
    )
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Inventory is archived")

    existing_inventory = data_provider_v2.fetch_inventory_pool().get_inventory(
        inventory_id
    )

    valid_keys = Inventory.model_fields.keys()
    update_data = {key: value for key, value in inventory.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_inventory, key, value)

    partial_updated_inventory = (
        data_provider_v2.fetch_inventory_pool().update_inventory(
            inventory_id, existing_inventory
        )
    )
    return partial_updated_inventory


@inventory_router_v2.patch("/{inventory_id}/unarchive")
def unarchive_inventory(inventory_id: int):

    inventory_pool = data_provider_v2.fetch_inventory_pool()

    is_archived = inventory_pool.is_inventory_archived(inventory_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="inventory is not archived")

    unarchived_inventory = inventory_pool.unarchive_inventory(inventory_id)
    return unarchived_inventory


@inventory_router_v2.delete("/{inventory_id}")
def archive_inventory(inventory_id: int):

    inventory_pool = data_provider_v2.fetch_inventory_pool()

    is_archived = inventory_pool.is_inventory_archived(inventory_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="inventory is already archived")

    archived_inventory = inventory_pool.archive_inventory(inventory_id)
    return archived_inventory
