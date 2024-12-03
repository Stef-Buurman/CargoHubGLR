import pytest
import httpx
from test_globals import *

test_warehouse = {
    "id": 99999999999999999,
    "code": "YQZZNL56",
    "name": "Heemskerk cargo hub",
    "address": "Karlijndreef 281",
    "zip": "4002 AS",
    "city": "Heemskerk",
    "province": "Friesland",
    "country": "NL",
    "contact_name": "Fem Keijzer",
    "contact_phone": "(078) 0013363",
    "contact_email": "blamore@example.net",
    "created_at": "1983-04-13 04:59:55",
    "updated_at": "2007-02-08 20:11:00",
}

test_location = {
    "id": 99999999999999999,
    "warehouse_id": 99999999999999999,
    "code": "A.1.0",
    "name": "Row: A, Rack: 1, Shelf: 0",
    "created_at": "1992-05-15 03:21:32",
    "updated_at": "1992-05-15 03:21:32",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_warehouses(client):
    response = client.get("/warehouses/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_warehouses_no_api_key(client):
    response = client.get("/warehouses/")
    assert response.status_code == 403


def test_get_all_warehouses_invalid_api_key(client):
    response = client.get("/warehouses/", headers=invalid_headers)
    assert response.status_code == 403


def test_get_locations_by_warehouse_id(client):
    response = client.post("/warehouses/", json=test_warehouse, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_warehouse["id"] = response.json()["id"]
    assert response.json()["id"] == test_warehouse["id"]

    response = client.post("/locations/", json=test_location, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_location["id"] = response.json()["id"]
    assert response.json()["id"] == test_location["id"]

    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

    response = client.delete(
        f"/warehouses/{test_warehouse['id']}", headers=test_headers
    )
    assert response.status_code == 200

    response = client.delete(f"/locations/{test_location['id']}", headers=test_headers)
    assert response.status_code == 200


def test_get_locations_by_warehouse_id_no_api_key(client):
    response = client.get(f"/warehouses/{test_warehouse['id']}/locations")
    assert response.status_code == 403


def test_get_locations_by_warehouse_id_invalid_api_key(client):
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations", headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_locations_by_nonexistent_warehouse_id(client):
    response = client.get(
        f"/warehouses/{non_existent_id}/locations", headers=test_headers
    )
    assert response.status_code == 404


def test_get_locations_by_invalid_warehouse_id(client):
    response = client.get("/warehouses/invalid_id/locations", headers=test_headers)
    assert response.status_code == 422


# def test_get_locations_by_warehouse_id_no_locations(client):
#     response = client.get(
#         f"/warehouses/{test_warehouse['id']}/locations", headers=test_headers
#     )
#     assert response.status_code == 404


def test_add_warehouse(client):
    response = client.post("/warehouses/", json=test_warehouse, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_warehouse["id"] = response.json()["id"]
    assert response.json()["id"] == test_warehouse["id"]


def test_add_warehouse_no_api_key(client):
    response = client.post("/warehouses/", json=test_warehouse)
    assert response.status_code == 403


def test_add_warehouse_invalid_api_key(client):
    response = client.post("/warehouses/", json=test_warehouse, headers=invalid_headers)
    assert response.status_code == 403


# def test_add_existing_warehouse(client):
#     response = client.post("/warehouses/", json=test_warehouse, headers=test_headers)
#     assert response.status_code == 409


def test_get_warehouse_by_id(client):
    response = client.get(
        "/warehouses/" + str(test_warehouse["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json is not None
    assert isinstance(response_json, dict)


def test_get_warehouse_no_api_key(client):
    response = client.get("/warehouses/" + str(test_warehouse["id"]))
    assert response.status_code == 403


def test_get_warehouse_invalid_api_key(client):
    response = client.get(
        "/warehouses/" + str(test_warehouse["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_nonexistent_warehouse(client):
    response = client.get(f"/warehouses/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_get_invalid_warehouse_id(client):
    response = client.get("/warehouses/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_update_warehouse(client):
    updated_warehouse = test_warehouse
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_warehouse["id"]),
        json=updated_warehouse,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_warehouse["id"]), headers=test_headers
    )
    assert response_get.status_code == 200
    response_json = response_get.json()
    assert response_json is not None
    assert response_json["name"] == updated_warehouse["name"]


def test_update_warehouse_no_api_key(client):
    updated_warehouse = test_warehouse
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_warehouse["id"]), json=updated_warehouse
    )
    assert response.status_code == 403


def test_update_warehouse_invalid_api_key(client):
    updated_warehouse = test_warehouse
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_warehouse["id"]),
        json=updated_warehouse,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_update_nonexistent_warehouse(client):
    updated_warehouse = test_warehouse
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(non_existent_id),
        json=updated_warehouse,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_update_invalid_warehouse_id(client):
    updated_warehouse = test_warehouse
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/invalid_id", json=updated_warehouse, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_warehouse(client):
    updated_warehouse = {"name": "Updated Warehouse"}
    response = client.patch(
        "/warehouses/" + str(test_warehouse["id"]),
        json=updated_warehouse,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_warehouse["id"]), headers=test_headers
    )
    assert response_get.status_code == 200
    response_json = response_get.json()
    assert response_json is not None
    assert response_json["name"] == updated_warehouse["name"]


def test_partial_update_warehouse_no_api_key(client):
    updated_warehouse = {"name": "Updated Warehouse"}
    response = client.patch(
        "/warehouses/" + str(test_warehouse["id"]), json=updated_warehouse
    )
    assert response.status_code == 403


def test_partial_update_warehouse_invalid_api_key(client):
    updated_warehouse = {"name": "Updated Warehouse"}
    response = client.patch(
        "/warehouses/" + str(test_warehouse["id"]),
        json=updated_warehouse,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_nonexistent_warehouse(client):
    updated_warehouse = {"name": "Updated Warehouse"}
    response = client.patch(
        "/warehouses/" + str(non_existent_id),
        json=updated_warehouse,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_partial_update_invalid_warehouse_id(client):
    updated_warehouse = {"name": "Updated Warehouse"}
    response = client.patch(
        "/warehouses/invalid_id", json=updated_warehouse, headers=test_headers
    )
    assert response.status_code == 422


def test_delete_warehouse(client):
    response = client.delete(
        "/warehouses/" + str(test_warehouse["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_warehouse["id"]), headers=test_headers
    )
    assert response_get.status_code == 404


def test_delete_warehouse_no_api_key(client):
    response = client.delete("/warehouses/" + str(test_warehouse["id"]))
    assert response.status_code == 403


def test_delete_warehouse_invalid_api_key(client):
    response = client.delete(
        "/warehouses/" + str(test_warehouse["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
