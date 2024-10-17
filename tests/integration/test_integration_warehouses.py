import pytest
import httpx
from test_globals import MAIN_URL, non_existent_id, test_headers, invalid_headers

test_data = {
    "id": 99999999999999999,
    "code": "YQZZNL56",
    "name": "Heemskerk cargo hub",
    "address": "Karlijndreef 281",
    "zip": "4002 AS",
    "city": "Heemskerk",
    "province": "Friesland",
    "country": "NL",
    "contact": {
        "name": "Fem Keijzer",
        "phone": "(078) 0013363",
        "email": "blamore@example.net",
    },
    "created_at": "1983-04-13 04:59:55",
    "updated_at": "2007-02-08 20:11:00",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL) as client:
        yield client


def test_get_all_warehouses(client):
    response = client.get("/warehouses/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_warehouses_no_api_key(client):
    response = client.get("/warehouses/")
    assert response.status_code == 403


def test_get_all_warehouses_invalid_api_key(client):
    response = client.get("/warehouses/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_warehouse(client):
    response = client.post("/warehouses/", json=test_data, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200


def test_add_warehouse_no_api_key(client):
    response = client.post("/warehouses/", json=test_data)
    assert response.status_code == 403


def test_add_warehouse_invalid_api_key(client):
    response = client.post("/warehouses/", json=test_data, headers=invalid_headers)
    assert response.status_code == 403


def test_get_warehouse_by_id(client):
    response = client.get("/warehouses/" + str(test_data["id"]), headers=test_headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json is not None
    assert isinstance(response_json, dict)


def test_get_warehouse_no_api_key(client):
    response = client.get("/warehouses/" + str(test_data["id"]))
    assert response.status_code == 403


def test_get_warehouse_invalid_api_key(client):
    response = client.get(
        "/warehouses/" + str(test_data["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_nonexistent_warehouse(client):
    response = client.get(f"/warehouses/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_get_nonexistent_warehouse_no_api_key(client):
    response = client.get(f"/warehouses/{non_existent_id}")
    assert response.status_code == 403


def test_get_nonexistent_warehouse_invalid_api_key(client):
    response = client.get(f"/warehouses/{non_existent_id}", headers=invalid_headers)
    assert response.status_code == 403


def test_update_warehouse(client):
    updated_warehouse = test_data
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_data["id"]),
        json=updated_warehouse,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_data["id"]), headers=test_headers
    )
    assert response_get.status_code == 200
    response_json = response_get.json()
    assert response_json is not None
    assert response_json["name"] == updated_warehouse["name"]


def test_update_warehouse_no_api_key(client):
    updated_warehouse = test_data
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put("/warehouses/" + str(test_data["id"]), json=updated_warehouse)
    assert response.status_code == 403


def test_update_warehouse_invalid_api_key(client):
    updated_warehouse = test_data
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_data["id"]),
        json=updated_warehouse,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_delete_warehouse(client):
    response = client.delete(
        "/warehouses/" + str(test_data["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_data["id"]), headers=test_headers
    )
    assert response_get.status_code == 404


def test_delete_warehouse_no_api_key(client):
    response = client.delete("/warehouses/" + str(test_data["id"]))
    assert response.status_code == 403


def test_delete_warehouse_invalid_api_key(client):
    response = client.delete(
        "/warehouses/" + str(test_data["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
