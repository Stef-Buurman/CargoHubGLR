from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.v2.item_line import ItemLine
from services import data_provider_v2, auth_provider_v2

item_line_router_v2 = APIRouter()


@item_line_router_v2.get("/")
def read_item_lines(api_key: str = Depends(auth_provider_v2.get_api_key)):
    data_provider_v2.init()
    item_lines = data_provider_v2.fetch_item_line_pool().get_item_lines()
    if item_lines is None:
        raise HTTPException(status_code=404, detail="Item lines not found")
    return item_lines


@item_line_router_v2.get("/{item_line_id}")
def read_item_line(
    item_line_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_line = data_provider_v2.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    return item_line


@item_line_router_v2.get("/{item_line_id}/items")
def read_items_for_item_line(
    item_line_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()

    item_line = data_provider_v2.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    items_for_item_line = data_provider_v2.fetch_item_pool().get_items_for_item_line(
        item_line_id
    )
    # if not items_for_item_line:
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
    return items_for_item_line


@item_line_router_v2.post("/")
def create_item(
    item_line: ItemLine, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    existingItem = data_provider_v2.fetch_item_line_pool().get_item_line(item_line.id)
    if existingItem is not None:
        raise HTTPException(status_code=409, detail="Item line already exists")
    added_item_line = data_provider_v2.fetch_item_line_pool().add_item_line(item_line)
    data_provider_v2.fetch_item_line_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=added_item_line.model_dump()
    )


@item_line_router_v2.put("/{item_line_id}")
def update_item(
    item_line_id: int,
    item_line: ItemLine,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingItem = data_provider_v2.fetch_item_line_pool().get_item_line(item_line_id)
    if existingItem is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    updated_item_line = data_provider_v2.fetch_item_line_pool().update_item_line(
        item_line_id, item_line
    )
    data_provider_v2.fetch_item_line_pool().save()
    return updated_item_line


@item_line_router_v2.patch("/{item_line_id}")
def partial_update_item_line(
    item_line_id: int,
    item_line: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_item_line = data_provider_v2.fetch_item_line_pool().get_item_line(
        item_line_id
    )
    if existing_item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    valid_keys = ItemLine.model_fields.keys()
    update_data = {key: value for key, value in item_line.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_item_line, key, value)

    partial_updated_item_line = (
        data_provider_v2.fetch_item_line_pool().update_item_line(
            item_line_id, existing_item_line
        )
    )
    data_provider_v2.fetch_item_line_pool().save()
    return partial_updated_item_line


@item_line_router_v2.delete("/{item_line_id}")
def delete_item(
    item_line_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    item_line_pool = data_provider_v2.fetch_item_line_pool()

    item_line = item_line_pool.get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    item_line_pool.remove_item_line(item_line_id)
    item_line_pool.save()
    return {"message": "Item line deleted successfully"}
