import httpx
import pytest
from tests.integration.test_globals import *

test_inventory = {
    "id": 99999999999999999,
    "item_id": "P000008",
    "description": "Multi-layered intangible artificial intelligence",
    "item_reference": "aro81493o",
    "locations": [27132, 11010, 10381, 34058, 31838, 21993, 9540],
    "total_on_hand": 159,
    "total_expected": 0,
    "total_ordered": 91,
    "total_allocated": 5,
    "total_available": 63,
    "created_at": "1986-10-17 07:19:42",
    "updated_at": "1989-03-30 17:53:04",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_inventories(client):
    response = client.get("/inventories/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_inventories_no_api_key(client):
    response = client.get("/inventories/")
    assert response.status_code == 403


def test_get_all_inventories_invalid_api_key(client):
    response = client.get("/inventories/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_inventory_no_api_key(client):
    response = client.post("/inventories/", json=test_inventory)
    assert response.status_code == 403
    responseGet = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_inventory_invalid_api_key(client):
    response = client.post(
        "/inventories/", json=test_inventory, headers=invalid_headers
    )
    assert response.status_code == 403
    responseGet = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_inventory(client):
    response = client.post("/inventories/", json=test_inventory, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_inventory["id"] = response.json()["id"]


def test_add_existing_inventory(client):
    response = client.post("/inventories/", json=test_inventory, headers=test_headers)
    assert response.status_code == 409


def test_get_inventory_by_id(client):
    response = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_inventory["id"]


def test_get_inventory_no_api_key(client):
    response = client.get("/inventories/" + str(test_inventory["id"]))
    assert response.status_code == 403


def test_get_inventory_invalid_api_key(client):
    response = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_invalid_inventory_id(client):
    response = client.get("/inventories/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_get_nonexistent_inventory(client):
    response = client.get(f"/inventories/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_update_inventory_no_api_key(client):
    updated_inventory = test_inventory.copy()
    updated_inventory["total_available"] = test_inventory["total_available"] + 100
    response = client.put(
        "/inventories/" + str(test_inventory["id"]), json=updated_inventory
    )
    assert response.status_code == 403
    response_get_inventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200
    assert (
        response_get_inventory.json()["total_available"]
        == test_inventory["total_available"]
    )


def test_update_inventory_invalid_api_key(client):
    updated_inventory = test_inventory.copy()
    updated_inventory["total_available"] = updated_inventory["total_available"] + 200
    response = client.put(
        "/inventories/" + str(updated_inventory["id"]),
        json=updated_inventory,
        headers=test_headers,
    )
    assert response.json()["total_available"] == updated_inventory["total_available"]
    assert response.status_code == 200
    response_get_inventory = client.get(
        "/inventories/" + str(updated_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200
    assert (
        response_get_inventory.json()["total_available"]
        == updated_inventory["total_available"]
    )

def test_update_inventory_locations(client):
    updated_inventory = test_inventory.copy()
    updated_inventory["locations"] = [9540]
    response = client.put(
        "/inventories/" + str(updated_inventory["id"]),
        json=updated_inventory,
        headers=test_headers,
    )
    assert response.json()["total_available"] == updated_inventory["total_available"]
    assert response.status_code == 200
    response_get_inventory = client.get(
        "/inventories/" + str(updated_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200
    assert (
        response_get_inventory.json()["locations"][0]
        == updated_inventory["locations"][0]
    )


def test_partial_update_inventory_no_api_key(client):
    updated_inventory = {"total_available": test_inventory["total_available"] + 100}
    response = client.patch(
        "/inventories/" + str(test_inventory["id"]), json=updated_inventory
    )
    assert response.status_code == 403


def test_partial_update_inventory_invalid_api_key(client):
    updated_inventory = {"total_available": test_inventory["total_available"] + 100}
    response = client.patch(
        "/inventories/" + str(test_inventory["id"]),
        json=updated_inventory,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_invalid_inventory_id(client):
    updated_inventory = {"total_available": test_inventory["total_available"] + 100}
    response = client.patch(
        "/inventories/invalid_id", json=updated_inventory, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_nonexistent_inventory(client):
    updated_inventory = {"total_available": test_inventory["total_available"] + 100}
    response = client.patch(
        f"/inventories/{non_existent_id}", json=updated_inventory, headers=test_headers
    )
    assert response.status_code == 404


def test_partial_update_inventory(client):
    updated_inventory = {"total_available": test_inventory["total_available"] + 100}
    response = client.patch(
        "/inventories/" + str(test_inventory["id"]),
        json=updated_inventory,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_inventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200
    assert (
        response_get_inventory.json()["total_available"]
        == updated_inventory["total_available"]
    )


def test_delete_inventory_no_api_key(client):
    response = client.delete("/inventories/" + str(test_inventory["id"]))
    assert response.status_code == 403
    response_get_inventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200


def test_delete_inventory_invalid_api_key(client):
    response = client.delete(
        "/inventories/" + str(test_inventory["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_inventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 200


def test_delete_inventory(client):
    response = client.delete(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_inventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert response_get_inventory.status_code == 404
