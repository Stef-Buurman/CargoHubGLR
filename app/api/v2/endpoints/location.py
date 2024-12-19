from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2 import data_provider_v2
from models.v2.location import Location

location_router_v2 = APIRouter(tags=["v2.Locations"], prefix="/locations")


@location_router_v2.get("/{location_id}")
def read_location(location_id: int):
    location = data_provider_v2.fetch_location_pool().get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    return location


@location_router_v2.get("")
def read_locations(request: Request):
    locations = data_provider_v2.fetch_location_pool().get_locations()
    if locations is None:
        raise HTTPException(status_code=404, detail="No locations found")
    return request.state.pagination.apply(locations)


@location_router_v2.post("")
def create_location(location: Location):
    created_location = data_provider_v2.fetch_location_pool().add_location(location)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_location.model_dump()
    )


@location_router_v2.put("/{location_id}")
def update_location(location_id: int, location: Location):
    existing_location = data_provider_v2.fetch_location_pool().get_location(location_id)
    if existing_location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    updated_location = data_provider_v2.fetch_location_pool().update_location(
        location_id, location
    )
    return updated_location


@location_router_v2.patch("/{location_id}")
def partial_update_location(location_id: int, location: dict):
    existing_location = data_provider_v2.fetch_location_pool().get_location(location_id)
    if existing_location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    valid_keys = Location.model_fields.keys()
    update_data = {key: value for key, value in location.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_location, key, value)

    partial_updated_location = data_provider_v2.fetch_location_pool().update_location(
        location_id, existing_location
    )
    return partial_updated_location


@location_router_v2.delete("/{location_id}")
def archive_location(location_id: int):
    location = data_provider_v2.fetch_location_pool().is_location_archived(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    elif location:
        raise HTTPException(
            status_code=400,
            detail=f"Location with id {location_id} is already archived",
        )
    data_provider_v2.fetch_location_pool().archive_location(location_id)
    return {"message": "Location archived successfully"}


@location_router_v2.patch("/{location_id}/unarchive")
def unarchive_location(location_id: int):
    existing_location = data_provider_v2.fetch_location_pool().is_location_archived(
        location_id
    )
    if existing_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    elif not existing_location:
        raise HTTPException(
            status_code=400,
            detail=f"Location with id {location_id} is not archived",
        )
    data_provider_v2.fetch_location_pool().unarchive_location(location_id)
    return {"message": "Location unarchived successfully"}
