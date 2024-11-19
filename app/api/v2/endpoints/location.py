from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider
from models.v2.location import Location

location_router_v2 = APIRouter()


@location_router_v2.get("/{location_id}")
def read_location(location_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    location = data_provider_v2.fetch_location_pool().get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    return location


@location_router_v2.get("/")
def read_locations(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    locations = data_provider_v2.fetch_location_pool().get_locations()
    if locations is None:
        raise HTTPException(status_code=404, detail="No locations found")
    return locations


@location_router_v2.post("/")
def create_location(
    location: Location, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    existing_location = data_provider_v2.fetch_location_pool().get_location(location.id)
    if existing_location is not None:
        raise HTTPException(
            status_code=409, detail=f"Location with id {location.id} already exists"
        )
    created_location = data_provider_v2.fetch_location_pool().add_location(location)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_location.model_dump()
    )


@location_router_v2.put("/{location_id}")
def update_location(
    location_id: int,
    location: Location,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider_v2.init()
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
def partial_update_location(
    location_id: int,
    location: dict,
    api_key: str = Depends(auth_provider.get_api_key),
):
    data_provider_v2.init()
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
def delete_location(
    location_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    location = data_provider_v2.fetch_location_pool().get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    data_provider_v2.fetch_location_pool().remove_location(location_id)
    return {"message": "Location deleted successfully"}
