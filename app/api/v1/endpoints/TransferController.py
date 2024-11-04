from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.services import data_provider, auth_provider

transfer_router = APIRouter()


@transfer_router.get("/{transfer_id}")
def read_transfer(transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    transfer = data_provider.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@transfer_router.get("/")
def read_transfers(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    transfers = data_provider.fetch_transfer_pool().get_transfers()
    if transfers is None:
        raise HTTPException(status_code=404, detail="No transfers found")
    return transfers


@transfer_router.get("/{transfer_id}/items")
def read_transfer_items(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    transfer = data_provider.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    items = data_provider.fetch_transfer_pool().get_items_in_transfer(transfer_id)
    if items is None:
        raise HTTPException(status_code=404, detail="No items found in transfer")
    return items


@transfer_router.post("/")
def create_transfer(transfer: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existing_transfer = data_provider.fetch_transfer_pool().get_transfer(transfer["id"])
    if existing_transfer is not None:
        raise HTTPException(status_code=409, detail="Transfer already exists")
    data_provider.fetch_transfer_pool().add_transfer(transfer)
    data_provider.fetch_transfer_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=transfer)


@transfer_router.put("/{transfer_id}")
def update_transfer(
    transfer_id: int, transfer: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existing_transfer = data_provider.fetch_transfer_pool().get_transfer(transfer_id)
    if existing_transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    data_provider.fetch_transfer_pool().update_transfer(transfer_id, transfer)
    data_provider.fetch_transfer_pool().save()
    return transfer


@transfer_router.put("/{transfer_id}/commit")
def commit_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    transfer = data_provider.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    for x in transfer["items"]:
        inventories = data_provider.fetch_inventory_pool().get_inventories_for_item(
            x["item_id"]
        )

        for y in inventories:
            if y["location_id"] == transfer["transfer_from"]:
                y["total_on_hand"] -= x["amount"]
                y["total_expected"] = y["total_on_hand"] + y["total_ordered"]
                y["total_available"] = y["total_on_hand"] - y["total_allocated"]
                data_provider.fetch_inventory_pool().update_inventory(y["id"], y)
            elif y["location_id"] == transfer["transfer_to"]:
                y["total_on_hand"] += x["amount"]
                y["total_expected"] = y["total_on_hand"] + y["total_ordered"]
                y["total_available"] = y["total_on_hand"] - y["total_allocated"]
                data_provider.fetch_inventory_pool().update_inventory(y["id"], y)
    transfer["transfer_status"] = "Processed"
    data_provider.fetch_transfer_pool().update_transfer(transfer_id, transfer)
    data_provider.fetch_transfer_pool().save()
    data_provider.fetch_inventory_pool().save()
    return {"message": "Transfer committed successfully"}


@transfer_router.delete("/{transfer_id}")
def delete_transfer(
    transfer_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    transfer = data_provider.fetch_transfer_pool().get_transfer(transfer_id)
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    data_provider.fetch_transfer_pool().remove_transfer(transfer_id)
    data_provider.fetch_transfer_pool().save()
    return {"message": "Transfer deleted successfully"}
