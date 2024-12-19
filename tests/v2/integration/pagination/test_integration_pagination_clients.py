import pytest
import httpx
from test_globals import *


test_CargoClient = {
    "id": 999999999,
    "name": "Raymond Inc",
    "address": "1296 Daniel Road Apt. 349",
    "city": "Pierceview",
    "zip_code": "28301",
    "province": "Colorado",
    "country": "United States",
    "contact_name": "Bryan Clark",
    "contact_phone": "242.732.3483x2573",
    "contact_email": "robertcharles@example.net",
    "created_at": "2010-04-28 02:22:53",
    "updated_at": "2022-02-09 20:22:35",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_clients_page_1(client):
    response = client.get(f"/clients{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_clients_page_2(client):
    response = client.get(f"/clients{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_clients_page_0(client):
    response = client.get(f"/clients{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_clients_page_negative(client):
    response = client.get(f"/clients{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_clients_page_too_high(client):
    response_clients = client.get("/clients", headers=test_headers)
    assert response_clients.status_code == 200
    response = client.get(
        "/clients/page" + str(response_clients.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_clients_wrong_page_number(client):
    response = client.get("/clients" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/clients" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/clients" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/clients" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_client_orders_page_1(client):
    add_response = client.post("/clients", json=test_CargoClient, headers=test_headers)
    assert add_response.status_code in [200, 201]
    test_CargoClient["id"] = add_response.json()["id"]
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_client_orders_page_0(client):
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_client_orders_page_negative(client):
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_client_orders_page_too_high(client):
    response_orders = client.get(
        f"/clients/{test_CargoClient['id']}/orders", headers=test_headers
    )
    assert response_orders.status_code == 200
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders/page/{response_orders.json()['pagination']['pages'] + 1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_client_orders_wrong_page_number(client):
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{wrong_page_1}",
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{wrong_page_2}",
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{wrong_page_3}",
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/clients/{test_CargoClient['id']}/orders{wrong_page_4}",
        headers=test_headers,
    )
    assert response.status_code == 422
    remove_response = client.delete(
        f"/clients/{test_CargoClient['id']}", headers=test_headers
    )
    assert remove_response.status_code == 200
