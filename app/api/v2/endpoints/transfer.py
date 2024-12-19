from fastapi import APIRouter, HTTPException, Request
from services.v2 import data_provider_v2
from models.v2.transfer import Transfer

transfer_router_v2 = APIRouter(tags=["v2.Transfers"], prefix="/transfers")


@transfer_router_v2.get("/{transfer_id}")
def read_transfer(transfer_id: int):
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@transfer_router_v2.get("")
def read_transfers(request: Request):
    transfers = data_provider_v2.fetch_transfer_pool().get_transfers()
    if transfers is None:
        raise HTTPException(status_code=404, detail="No transfers found")
    return request.state.pagination.apply(transfers)


@transfer_router_v2.get("/{transfer_id}/items")
def read_transfer_items(transfer_id: int, request: Request):
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    items = data_provider_v2.fetch_transfer_pool().get_items_in_transfer(transfer_id)
    if items is None:
        raise HTTPException(status_code=404, detail="No items found in transfer")
    return request.state.pagination.apply(items)


@transfer_router_v2.post("")
def create_transfer(transfer: Transfer):
    created_transfer = data_provider_v2.fetch_transfer_pool().add_transfer(transfer)
    return created_transfer


@transfer_router_v2.put("/{transfer_id}")
def update_transfer(transfer_id: int, transfer: Transfer):
    existing_transfer = data_provider_v2.fetch_transfer_pool().is_transfer_archived(
        transfer_id
    )
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    elif existing_transfer:
        raise HTTPException(status_code=400, detail="Transfer is archived")
    updated_transfer = data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, transfer
    )
    return updated_transfer


@transfer_router_v2.patch("/{transfer_id}")
def partial_update_transfer(transfer_id: int, transfer: dict):
    existing_transfer = data_provider_v2.fetch_transfer_pool().is_transfer_archived(
        transfer_id
    )
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    elif existing_transfer:
        raise HTTPException(status_code=400, detail="Transfer is archived")
    existing_transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)

    valid_keys = Transfer.model_fields.keys()
    update_data = {key: value for key, value in transfer.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_transfer, key, value)

    partial_updated_transfer = data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, existing_transfer
    )
    return partial_updated_transfer


@transfer_router_v2.put("/{transfer_id}/commit")
def commit_transfer(transfer_id: int):
    transfer = data_provider_v2.fetch_transfer_pool().is_transfer_archived(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    elif transfer:
        raise HTTPException(status_code=400, detail="Transfer is archived")
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)

    committed_transfer = data_provider_v2.fetch_transfer_pool().commit_transfer(
        transfer
    )
    data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, committed_transfer
    )
    return {"message": "Transfer committed successfully"}


@transfer_router_v2.delete("/{transfer_id}")
def archive_transfer(transfer_id: int):
    transfer = data_provider_v2.fetch_transfer_pool().is_transfer_archived(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    elif transfer:
        raise HTTPException(status_code=400, detail="Transfer is already archived")
    data_provider_v2.fetch_transfer_pool().archive_transfer(transfer_id)
    return {"message": "Transfer archived successfully"}


@transfer_router_v2.patch("/{transfer_id}/unarchive")
def unarchive_transfer(transfer_id: int):
    transfer = data_provider_v2.fetch_transfer_pool().is_transfer_archived(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    elif not transfer:
        raise HTTPException(status_code=400, detail="Transfer is not archived")
    data_provider_v2.fetch_transfer_pool().unarchive_transfer(transfer_id)
    return {"message": "Transfer unarchived successfully"}
