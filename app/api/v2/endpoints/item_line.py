from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from models.v2.item_line import ItemLine
from services.v2 import data_provider_v2
from utils.globals import pagination_url

item_line_router_v2 = APIRouter(tags=["v2.Item Lines"], prefix="/item_lines")


@item_line_router_v2.get("/{item_line_id}")
def read_item_line(item_line_id: int):

    item_line = data_provider_v2.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    return item_line


@item_line_router_v2.get("/")
@item_line_router_v2.get(pagination_url)
def read_item_lines(pagination: Pagination = Depends()):

    item_lines = data_provider_v2.fetch_item_line_pool().get_item_lines()
    if item_lines is None:
        raise HTTPException(status_code=404, detail="Item lines not found")
    return pagination.apply(item_lines)


@item_line_router_v2.get("/{item_line_id}/items")
@item_line_router_v2.get("/{item_line_id}/items" + pagination_url)
def read_items_for_item_line(item_line_id: int, pagination: Pagination = Depends()):

    item_line = data_provider_v2.fetch_item_line_pool().get_item_line(item_line_id)
    if item_line is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )

    items_for_item_line = data_provider_v2.fetch_item_pool().get_items_for_item_line(
        item_line_id
    )
    return pagination.apply(items_for_item_line)


@item_line_router_v2.post("/")
def create_item(item_line: ItemLine):

    added_item_line = data_provider_v2.fetch_item_line_pool().add_item_line(item_line)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=added_item_line.model_dump()
    )


@item_line_router_v2.put("/{item_line_id}")
def update_item(item_line_id: int, item_line: ItemLine):

    is_archived = data_provider_v2.fetch_item_line_pool().is_item_line_archived(
        item_line_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Item line is archived")

    updated_item_line = data_provider_v2.fetch_item_line_pool().update_item_line(
        item_line_id, item_line
    )
    return updated_item_line


@item_line_router_v2.patch("/{item_line_id}")
def partial_update_item_line(item_line_id: int, item_line: dict):

    is_archived = data_provider_v2.fetch_item_line_pool().is_item_line_archived(
        item_line_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Item line is archived")

    existing_item_line = data_provider_v2.fetch_item_line_pool().get_item_line(
        item_line_id
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
    return partial_updated_item_line


@item_line_router_v2.patch("/{item_line_id}/unarchive")
def unarchive_item_line(item_line_id: int):

    is_archived = data_provider_v2.fetch_item_line_pool().is_item_line_archived(
        item_line_id
    )
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    elif is_archived is False:
        raise HTTPException(status_code=400, detail=f"Item line is not archived")

    updated_item_line = data_provider_v2.fetch_item_line_pool().unarchive_item_line(
        item_line_id
    )
    return updated_item_line


@item_line_router_v2.delete("/{item_line_id}")
def archive_item_line(item_line_id: int):

    item_line_pool = data_provider_v2.fetch_item_line_pool()

    is_archived = item_line_pool.is_item_line_archived(item_line_id)
    if is_archived is None:
        raise HTTPException(
            status_code=404, detail=f"Item line with id {item_line_id} not found"
        )
    elif is_archived is True:
        raise HTTPException(status_code=400, detail=f"Item line is already archived")

    updated_item_line = item_line_pool.archive_item_line(item_line_id)
    return updated_item_line
