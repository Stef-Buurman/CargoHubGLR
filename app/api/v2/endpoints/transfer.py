from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider_v2
from models.v2.transfer import Transfer

transfer_router_v2 = APIRouter()


@transfer_router_v2.get("/{transfer_id}")
def read_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@transfer_router_v2.get("/")
def read_transfers(api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    transfers = data_provider_v2.fetch_transfer_pool().get_transfers()
    if transfers is None:
        raise HTTPException(status_code=404, detail="No transfers found")
    return transfers


@transfer_router_v2.get("/{transfer_id}/items")
def read_transfer_items(
    transfer_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
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
    transfer: Transfer, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer.id)
    if existing_transfer is not None:
        raise HTTPException(status_code=409, detail="Transfer already exists")
    created_transfer = data_provider_v2.fetch_transfer_pool().add_transfer(transfer)
    data_provider_v2.fetch_transfer_pool().save()
    return created_transfer


@transfer_router_v2.put("/{transfer_id}")
def update_transfer(
    transfer_id: int,
    transfer: Transfer,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    updated_transfer = data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, transfer
    )
    data_provider_v2.fetch_transfer_pool().save()
    return updated_transfer


@transfer_router_v2.patch("/{transfer_id}")
def partial_update_transfer(
    transfer_id: int,
    transfer: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")

    for key, value in transfer.items():
        setattr(existing_transfer, key, value)

    partial_updated_transfer = data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, existing_transfer
    )
    data_provider_v2.fetch_transfer_pool().save()
    return partial_updated_transfer


@transfer_router_v2.put("/{transfer_id}/commit")
def commit_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    committed_transfer = data_provider_v2.fetch_transfer_pool().commit_transfer(
        transfer
    )
    data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, committed_transfer
    )
    data_provider_v2.fetch_transfer_pool().save()
    data_provider_v2.fetch_inventory_pool().save()

    return {"message": "Transfer committed successfully"}


@transfer_router_v2.delete("/{transfer_id}")
def delete_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    data_provider_v2.fetch_transfer_pool().remove_transfer(transfer_id)
    data_provider_v2.fetch_transfer_pool().save()
    return {"message": "Transfer deleted successfully"}
