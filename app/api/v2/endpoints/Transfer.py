from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider
from models.v2.transfer import Transfer

transfer_router_v2 = APIRouter()


@transfer_router_v2.get("/{transfer_id}")
def read_transfer(transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@transfer_router_v2.get("/")
def read_transfers(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    transfers = data_provider_v2.fetch_transfer_pool().get_transfers()
    if transfers is None:
        raise HTTPException(status_code=404, detail="No transfers found")
    return transfers


@transfer_router_v2.get("/{transfer_id}/items")
def read_transfer_items(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    items = data_provider_v2.fetch_transfer_pool().get_items_in_transfer(transfer_id)
    if items is None:
        raise HTTPException(status_code=404, detail="No items found in transfer")
    return items


@transfer_router_v2.post("/")
def create_transfer(
    transfer: Transfer, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer.id)
    if existing_transfer is not None:
        raise HTTPException(status_code=409, detail="Transfer already exists")
    data_provider_v2.fetch_transfer_pool().add_transfer(transfer)
    data_provider_v2.fetch_transfer_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=transfer.model_dump()
    )


@transfer_router_v2.put("/{transfer_id}")
def update_transfer(
    transfer_id: int,
    transfer: Transfer,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider_v2.init()
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    data_provider_v2.fetch_transfer_pool().update_transfer(transfer_id, transfer)
    data_provider_v2.fetch_transfer_pool().save()
    return transfer


@transfer_router_v2.put("/{transfer_id}/commit")
def commit_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    for x in transfer.items:
        inventories = data_provider_v2.fetch_inventory_pool().get_inventories_for_item(
            x.item_id
        )

        for y in inventories:
            if transfer.transfer_from in y["locations"]:
                y["total_on_hand"] -= x.amount
                y["total_expected"] = y["total_on_hand"] + y["total_ordered"]
                y["total_available"] = y["total_on_hand"] - y["total_allocated"]
                data_provider_v2.fetch_inventory_pool().update_inventory(y["id"], y)
            elif transfer.transfer_to in y["locations"]:
                y["total_on_hand"] += x.amount
                y["total_expected"] = y["total_on_hand"] + y["total_ordered"]
                y["total_available"] = y["total_on_hand"] - y["total_allocated"]
                data_provider_v2.fetch_inventory_pool().update_inventory(y["id"], y)

    transfer.transfer_status = "Processed"
    data_provider_v2.fetch_transfer_pool().update_transfer(transfer_id, transfer)
    data_provider_v2.fetch_transfer_pool().save()
    data_provider_v2.fetch_inventory_pool().save()

    return {"message": "Transfer committed successfully"}


@transfer_router_v2.delete("/{transfer_id}")
def delete_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    data_provider_v2.fetch_transfer_pool().remove_transfer(transfer_id)
    data_provider_v2.fetch_transfer_pool().save()
    return {"message": "Transfer deleted successfully"}
