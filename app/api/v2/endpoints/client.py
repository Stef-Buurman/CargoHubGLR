from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services import data_provider_v2, auth_provider
from models.v2.client import Client

client_router_v2 = APIRouter()


@client_router_v2.get("/{client_id}")
def read_client(client_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@client_router_v2.get("/")
def read_clients(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    clients = data_provider_v2.fetch_client_pool().get_clients()
    if clients is None:
        raise HTTPException(status_code=404, detail="No clients found")
    return clients


@client_router_v2.get("/{client_id}/orders")
def read_client_orders(
    client_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    orders = data_provider_v2.fetch_order_pool().get_orders_for_client(client_id)
    if orders is None:
        raise HTTPException(status_code=404, detail="No orders found for client")
    return orders


@client_router_v2.post("/")
def create_client(client: Client, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    existing_client = data_provider_v2.fetch_client_pool().get_client(client.id)
    if existing_client is not None:
        raise HTTPException(status_code=409, detail="Client already exists")
    created_client = data_provider_v2.fetch_client_pool().add_client(client)
    data_provider_v2.fetch_client_pool().save()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_client.model_dump()
    )


@client_router_v2.put("/{client_id}")
def update_client(
    client_id: int, client: Client, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider_v2.init()
    existing_client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if existing_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    updated_client = data_provider_v2.fetch_client_pool().update_client(
        client_id, client
    )
    data_provider_v2.fetch_client_pool().save()
    return updated_client


@client_router_v2.delete("/{client_id}")
def delete_client(client_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider_v2.init()
    client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    data_provider_v2.fetch_client_pool().remove_client(client_id)
    data_provider_v2.fetch_client_pool().save()
    return {"message": "Client deleted successfully"}
