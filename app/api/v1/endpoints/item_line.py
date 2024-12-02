from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

item_line_router = APIRouter()


@item_line_router.get("/")
def read_item_lines(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    item_lines = data_provider.fetch_item_line_pool().get_item_lines()
    if item_lines is None:
        raise HTTPException(status_code=404, detail="Item lines not found")
    return item_lines


@item_line_router.get("/{item_line_id}")
def read_item_line(
    item_line_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    item_line = data_provider.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    return item_line


@item_line_router.get("/{item_line_id}/items")
def read_items_for_item_line(
    item_line_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()

    item_line = data_provider.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    items_for_item_line = data_provider.fetch_item_pool().get_items_for_item_line(
        item_line_id
    )
    return items_for_item_line


@item_line_router.post("/")
def create_item(item_line: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existingItem = data_provider.fetch_item_line_pool().get_item_line(item_line["id"])
    if existingItem is not None:
        raise HTTPException(status_code=409, detail="Item line already exists")
    data_provider.fetch_item_line_pool().add_item_line(item_line)
    data_provider.fetch_item_line_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item_line)


@item_line_router.put("/{item_line_id}")
def update_item(
    item_line_id: int,
    item_line: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider.init()
    existingItem = data_provider.fetch_item_line_pool().get_item_line(item_line_id)
    if existingItem is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    data_provider.fetch_item_line_pool().update_item_line(item_line_id, item_line)
    data_provider.fetch_item_line_pool().save()
    return item_line


@item_line_router.delete("/{item_line_id}")
def delete_item(item_line_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    item_line_pool = data_provider.fetch_item_line_pool()

    item_line = item_line_pool.get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    item_line_pool.remove_item_line(item_line_id)
    item_line_pool.save()
    return {"message": "Item line deleted successfully"}
