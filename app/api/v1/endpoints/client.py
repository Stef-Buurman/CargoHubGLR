from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

client_router = APIRouter(tags=["v1.Clients"], prefix="/clients")


@client_router.get("/{client_id}")
def read_client(client_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    client = data_provider.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@client_router.get("")
def read_clients(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    clients = data_provider.fetch_client_pool().get_clients()
    if clients is None:
        raise HTTPException(status_code=404, detail="No clients found")
    return clients


@client_router.get("/{client_id}/orders")
def read_client_orders(
    client_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    client = data_provider.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    orders = data_provider.fetch_order_pool().get_orders_for_client(client_id)
    if orders is None:
        raise HTTPException(status_code=404, detail="No orders found for client")
    return orders


@client_router.post("")
def create_client(client: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existing_client = data_provider.fetch_client_pool().get_client(client["id"])
    if existing_client is not None:
        raise HTTPException(status_code=409, detail="Client already exists")
    data_provider.fetch_client_pool().add_client(client)
    data_provider.fetch_client_pool().save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=client)


@client_router.put("/{client_id}")
def update_client(
    client_id: int, client: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existing_client = data_provider.fetch_client_pool().get_client(client_id)
    if existing_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    data_provider.fetch_client_pool().update_client(client_id, client)
    data_provider.fetch_client_pool().save()
    return client


@client_router.delete("/{client_id}")
def delete_client(client_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    client = data_provider.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    data_provider.fetch_client_pool().remove_client(client_id)
    data_provider.fetch_client_pool().save()
    return {"message": "Client deleted successfully"}
