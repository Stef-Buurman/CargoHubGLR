import httpx
import pytest
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


def test_get_all_CargoClients(client):
    response = client.get("/clients/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_CargoClients_no_api_key(client):
    response = client.get("/clients/")
    assert response.status_code == 403


def test_get_all_CargoClients_invalid_api_key(client):
    response = client.get("/clients/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_CargoClient_no_api_key(client):
    response = client.post("/clients/", json=test_CargoClient)
    assert response.status_code == 403
    responseGet = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_CargoClient_invalid_api_key(client):
    response = client.post("/clients/", json=test_CargoClient, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_CargoClient(client):
    response = client.post("/clients/", json=test_CargoClient, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_CargoClient["id"] = response.json()["id"]


def test_get_CargoClient_by_id(client):
    response = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_CargoClient["id"]


def test_get_CargoClient_no_api_key(client):
    response = client.get("/clients/" + str(test_CargoClient["id"]))
    assert response.status_code == 403


def test_get_CargoClient_invalid_api_key(client):
    response = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_invalid_CargoClient_id(client):
    response = client.get("/clients/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_get_nonexistent_CargoClient(client):
    response = client.get("/clients/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_orders_for_client(client):
    response = client.get(
        f'/clients/{test_CargoClient["id"]}/orders', headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_orders_for_nonexistent_client(client):
    response = client.get(f"/clients/{non_existent_id}/orders", headers=test_headers)
    assert response.status_code == 404


def test_get_orders_for_client_invalid_client_id(client):
    response = client.get("/clients/invalid_id/orders", headers=test_headers)
    assert response.status_code == 422


def test_get_orders_for_client_no_api_key(client):
    response = client.get(f'/clients/{test_CargoClient["id"]}/orders')
    assert response.status_code == 403


def test_get_orders_for_client_invalid_api_key(client):
    response = client.get(
        f'/clients/{test_CargoClient["id"]}/orders', headers=invalid_headers
    )
    assert response.status_code == 403


def test_update_CargoClient_no_api_key(client):
    updated_CargoClient = test_CargoClient.copy()
    updated_CargoClient["name"] = "Updated Inc"
    response = client.put(
        f"/clients/{test_CargoClient['id']}", json=updated_CargoClient
    )
    assert response.status_code == 403
    response_get_CargoClient = client.get(
        f"/clients/{test_CargoClient['id']}", headers=test_headers
    )
    assert response_get_CargoClient.status_code == 200
    assert response_get_CargoClient.json()["name"] == test_CargoClient["name"]


def test_update_CargoClient_invalid_api_key(client):
    updated_CargoClient = test_CargoClient.copy()
    updated_CargoClient["name"] = "Updated Inc"
    response = client.put(
        f"/clients/{test_CargoClient['id']}",
        json=updated_CargoClient,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_CargoClient = client.get(
        f"/clients/{test_CargoClient['id']}", headers=test_headers
    )
    assert response_get_CargoClient.status_code == 200
    assert response_get_CargoClient.json()["name"] == test_CargoClient["name"]


def test_update_invalid_CargoClient_id(client):
    updated_CargoClient = test_CargoClient.copy()
    updated_CargoClient["name"] = "Updated Inc"
    response = client.put(
        "/clients/invalid_id", json=updated_CargoClient, headers=test_headers
    )
    assert response.status_code == 422


def test_update_nonexistent_CargoClient(client):
    updated_CargoClient = test_CargoClient.copy()
    updated_CargoClient["name"] = "Updated Inc"
    response = client.put(
        f"/clients/{non_existent_id}", json=updated_CargoClient, headers=test_headers
    )
    assert response.status_code == 404


def test_update_CargoClient(client):
    updated_CargoClient = test_CargoClient.copy()
    updated_CargoClient["name"] = "Updated Inc"
    response = client.put(
        f"/clients/{test_CargoClient['id']}",
        json=updated_CargoClient,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_CargoClient = client.get(
        f"/clients/{test_CargoClient['id']}", headers=test_headers
    )
    assert response_get_CargoClient.status_code == 200
    assert response_get_CargoClient.json()["name"] == updated_CargoClient["name"]


def test_partial_update_CargoClient_no_api_key(client):
    updated_client = {"name": "Updated client"}
    response = client.patch(
        "/clients/" + str(test_CargoClient["id"]), json=updated_client
    )
    assert response.status_code == 403


def test_partial_update_CargoClient_invalid_api_key(client):
    updated_client = {"name": "Updated client"}
    response = client.patch(
        "/clients/" + str(test_CargoClient["id"]),
        json=updated_client,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_invalid_CargoClient_id(client):
    updated_CargoClient = {"name": "Updated Inc"}
    response = client.patch(
        "/clients/invalid_id", json=updated_CargoClient, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_nonexistent_CargoClient(client):
    updated_CargoClient = {"name": "Updated Inc"}
    response = client.patch(
        f"/clients/{non_existent_id}", json=updated_CargoClient, headers=test_headers
    )
    assert response.status_code == 404


def test_partial_update_CargoClient(client):
    updated_CargoClient = {"name": "Updated Inc"}
    response = client.patch(
        f"/clients/{test_CargoClient['id']}",
        json=updated_CargoClient,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_CargoClient = client.get(
        f"/clients/{test_CargoClient['id']}", headers=test_headers
    )
    assert response_get_CargoClient.status_code == 200
    assert response_get_CargoClient.json()["name"] == updated_CargoClient["name"]


def test_archive_CargoClient_no_api_key(client):
    response = client.delete("/clients/" + str(test_CargoClient["id"]))
    assert response.status_code == 403


def test_archive_CargoClient_invalid_api_key(client):
    response = client.delete(
        "/clients/" + str(test_CargoClient["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_archive_invalid_CargoClient_id(client):
    response = client.delete("/clients/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_archive_nonexistent_CargoClient(client):
    response = client.delete("/clients/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_archive_CargoClient(client):
    response = client.delete(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_CargoClient = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert response_get_CargoClient.json()["is_archived"] is True


def test_unarchive_CargoClient_no_api_key(client):
    response = client.put("/clients/" + str(test_CargoClient["id"]) + "/unarchive")
    assert response.status_code == 403


def test_unarchive_CargoClient_invalid_api_key(client):
    response = client.put(
        "/clients/" + str(test_CargoClient["id"]) + "/unarchive",
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_unarchive_invalid_CargoClient_id(client):
    response = client.put("/clients/invalid_id/unarchive", headers=test_headers)
    assert response.status_code == 422


def test_unarchive_nonexistent_CargoClient(client):
    response = client.put(
        "/clients/" + str(non_existent_id) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_CargoClient(client):
    response = client.put(
        "/clients/" + str(test_CargoClient["id"]) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 200
    response_get_CargoClient = client.get(
        "/clients/" + str(test_CargoClient["id"]), headers=test_headers
    )
    assert response_get_CargoClient.json()["is_archived"] is False
