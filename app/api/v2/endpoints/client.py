from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.client import Client
from utils.globals import pagination_url

client_router_v2 = APIRouter(tags=["v2.Clients"], prefix="/clients")


@client_router_v2.get("/{client_id}")
def read_client(client_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)):

    client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@client_router_v2.get("/")
@client_router_v2.get(pagination_url)
def read_clients(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):

    clients = data_provider_v2.fetch_client_pool().get_clients()
    if clients is None:
        raise HTTPException(status_code=404, detail="No clients found")
    return pagination.apply(clients)


@client_router_v2.get("/{client_id}/orders")
@client_router_v2.get("/{client_id}/orders" + pagination_url)
def read_client_orders(
    client_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):

    client = data_provider_v2.fetch_client_pool().get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    orders = data_provider_v2.fetch_order_pool().get_orders_for_client(client_id)
    if orders is None:
        raise HTTPException(status_code=404, detail="No orders found for client")
    return pagination.apply(orders)


@client_router_v2.post("/")
def create_client(client: Client, api_key: str = Depends(auth_provider_v2.get_api_key)):

    created_client = data_provider_v2.fetch_client_pool().add_client(client)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_client.model_dump()
    )


@client_router_v2.put("/{client_id}")
def update_client(
    client_id: int, client: Client, api_key: str = Depends(auth_provider_v2.get_api_key)
):

    is_archived = data_provider_v2.fetch_client_pool().is_client_archived(client_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Client not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Client is archived")
    updated_client = data_provider_v2.fetch_client_pool().update_client(
        client_id, client
    )
    return updated_client


@client_router_v2.patch("/{client_id}")
def partial_update_client(
    client_id: int,
    client: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):

    is_archived = data_provider_v2.fetch_client_pool().is_client_archived(client_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Client not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Client is archived")

    existing_client = data_provider_v2.fetch_client_pool().get_client(client_id)

    valid_keys = Client.model_fields.keys()
    update_data = {key: value for key, value in client.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_client, key, value)

    partial_updated_client = data_provider_v2.fetch_client_pool().update_client(
        client_id, existing_client
    )
    return partial_updated_client


@client_router_v2.patch("/{client_id}/unarchive")
def unarchive_client(
    client_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):

    is_archived = data_provider_v2.fetch_client_pool().is_client_archived(client_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Client not found")
    elif is_archived is False:
        raise HTTPException(status_code=400, detail="Client is not archived")
    unarchived_client = data_provider_v2.fetch_client_pool().unarchive_client(client_id)
    return unarchived_client


@client_router_v2.delete("/{client_id}")
def archive_client(
    client_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):

    is_archived = data_provider_v2.fetch_client_pool().is_client_archived(client_id)
    if is_archived is None:
        raise HTTPException(status_code=404, detail="Client not found")
    elif is_archived is True:
        raise HTTPException(status_code=400, detail="Client is already archived")
    archived_client = data_provider_v2.fetch_client_pool().archive_client(client_id)
    return archived_client
