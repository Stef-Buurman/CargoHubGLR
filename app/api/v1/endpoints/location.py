from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

location_router = APIRouter()


@location_router.get("/{location_id}")
def read_location(location_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    location = data_provider.fetch_location_pool().get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    return location


@location_router.get("/")
def read_locations(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    locations = data_provider.fetch_location_pool().get_locations()
    if locations is None:
        raise HTTPException(status_code=404, detail="No locations found")
    return locations


@location_router.post("/")
def create_location(location: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existing_location = data_provider.fetch_location_pool().get_location(location["id"])
    if existing_location is not None:
        raise HTTPException(
            status_code=409, detail=f"Location with id {location['id']} already exists"
        )
    data_provider.fetch_location_pool().add_location(location)
    data_provider.fetch_location_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=location)


@location_router.put("/{location_id}")
def update_location(
    location_id: int, location: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existing_location = data_provider.fetch_location_pool().get_location(location_id)
    if existing_location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    data_provider.fetch_location_pool().update_location(location_id, location)
    data_provider.fetch_location_pool().save()
    return JSONResponse(status_code=status.HTTP_200_OK, content=location)


@location_router.delete("/{location_id}")
def delete_location(
    location_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    location = data_provider.fetch_location_pool().get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    data_provider.fetch_location_pool().remove_location(location_id)
    data_provider.fetch_location_pool().save()
    return {"message": "Location deleted successfully"}
