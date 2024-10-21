from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from providers import data_provider, auth_provider

shipment_router = APIRouter()

@shipment_router.get("/{shipment_id}")
def read_shipment(shipment_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    shipment = data_provider.fetch_shipment_pool().get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail=f"Shipment with id {shipment_id} not found")
    return shipment

@shipment_router.get("/")
def read_shipments(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    shipments = data_provider.fetch_shipment_pool().get_shipments()
    if shipments is None:
        raise HTTPException(status_code=404, detail="No shipments found")
    return shipments

@shipment_router.post("/")
def create_shipment(shipment: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existingShipment = data_provider.fetch_shipment_pool().get_shipment(shipment["id"])
    if existingShipment is not None:
        raise HTTPException(status_code=409, detail="Shipment already exists")
    data_provider.fetch_shipment_pool().add_shipment(shipment)
    data_provider.fetch_shipment_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=shipment)

@shipment_router.put("/{shipment_id}")
def update_shipment(shipment_id: int, shipment: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()    
    existingShipment = data_provider.fetch_shipment_pool().get_shipment(shipment_id)
    if existingShipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    data_provider.fetch_shipment_pool().update_shipment(shipment_id, shipment)
    data_provider.fetch_shipment_pool().save()
    return shipment

@shipment_router.delete("/{shipment_id}")
def delete_shipment(shipment_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    shipment_pool = data_provider.fetch_shipment_pool()
    shipment = shipment_pool.get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment_pool.remove_shipment(shipment_id)
    shipment_pool.save()
    return {"massage": "Shipment deleted successfully"}