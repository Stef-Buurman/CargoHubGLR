import pytest
from fastapi.testclient import TestClient
from api.main import app

test_data = {
    "id": 116969,
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
    return TestClient(app)


def test_get_all_warehouses(client):
    response = client.get("/warehouses", headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_warehouse(client):
    response = client.post(
        "/warehouses", json=test_data, headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200


def test_get_warehouse_by_id(client):
    response = client.get(
        "/warehouses/" + str(test_data["id"]), headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json is not None
    assert isinstance(response_json, dict)


def test_get_nonexistent_warehouse(client):
    response = client.get(
        "/warehouses/9999", headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 404


def test_update_warehouse(client):
    updated_warehouse = test_data
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + str(test_data["id"]),
        json=updated_warehouse,
        headers={"API_KEY": "test_api_key"},
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_data["id"]), headers={"API_KEY": "test_api_key"}
    )
    assert response_get.status_code == 200
    response_json = response_get.json()
    assert response_json is not None
    assert response_json["name"] == updated_warehouse["name"]


def test_delete_warehouse(client):
    response = client.delete(
        "/warehouses/" + str(test_data["id"]), headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + str(test_data["id"]), headers={"API_KEY": "test_api_key"}
    )
    assert response_get.status_code == 404
