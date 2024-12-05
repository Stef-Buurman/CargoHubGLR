from fastapi import APIRouter, Depends, HTTPException
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.transfer import Transfer
from utils.globals import pagination_url

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
@transfer_router_v2.get(pagination_url)
def read_transfers(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    transfers = data_provider_v2.fetch_transfer_pool().get_transfers()
    if transfers is None:
        raise HTTPException(status_code=404, detail="No transfers found")
    return pagination.apply(transfers)


@transfer_router_v2.get("/{transfer_id}/items")
@transfer_router_v2.get("/{transfer_id}/items" + pagination_url)
def read_transfer_items(
    transfer_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    transfer = data_provider_v2.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    items = data_provider_v2.fetch_transfer_pool().get_items_in_transfer(transfer_id)
    if items is None:
        raise HTTPException(status_code=404, detail="No items found in transfer")
    return pagination.apply(items)


@transfer_router_v2.post("/")
def create_transfer(
    transfer: Transfer, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    created_transfer = data_provider_v2.fetch_transfer_pool().add_transfer(transfer)
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

    valid_keys = Transfer.model_fields.keys()
    update_data = {key: value for key, value in transfer.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_transfer, key, value)

    partial_updated_transfer = data_provider_v2.fetch_transfer_pool().update_transfer(
        transfer_id, existing_transfer
    )
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
    return {"message": "Transfer deleted successfully"}
