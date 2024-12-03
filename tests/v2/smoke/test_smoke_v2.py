import httpx
import pytest
from test_globals import *


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_CargoClients(client):
    response = client.get("/clients/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_inventories(client):
    response = client.get("/inventories/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_item_groups(client):
    response = client.get("/item_groups/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_item_lines(client):
    response = client.get("/item_lines/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_item_types(client):
    response = client.get("/item_types/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_items(client):
    response = client.get("/items/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_locations(client):
    response = client.get("/locations/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_orders(client):
    response = client.get("/orders/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_shipments(client):
    response = client.get("/shipments/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_suppliers(client):
    response = client.get("/suppliers/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_transfers(client):
    response = client.get("/transfers/", headers=test_headers)
    assert response.status_code == 200


def test_get_all_warehouses(client):
    response = client.get("/warehouses/", headers=test_headers)
    assert response.status_code == 200
