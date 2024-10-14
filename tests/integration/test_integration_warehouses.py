import subprocess
import time
import pytest
import httpx

main_url = "http://localhost:3000/api/v1"


@pytest.fixture(scope="session", autouse=True)
def start_api_server():
    process = subprocess.Popen(["python", "api/main.py"])
    time.sleep(1)

    yield

    process.terminate()
    process.wait()


test_data = {
    "id": 1,
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
    with httpx.Client(base_url=main_url) as client:
        yield client


def test_get_all_warehouses(client):
    response = client.get("/warehouses", headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_warehouse(client):
    response = client.post(
        "/warehouses", json=test_data, headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 201


def test_get_warehouse_by_id(client):
    response = client.get(
        "/warehouses/" + test_data["id"], headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)


def test_get_nonexistent_warehouse(client):
    response = client.get(
        "/warehouses/nonexistent_id", headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200
    assert response.json() is None


def test_update_warehouse(client):
    updated_warehouse = test_data
    updated_warehouse["name"] = "Updated Warehouse"
    response = client.put(
        "/warehouses/" + test_data["id"],
        json=updated_warehouse,
        headers={"API_KEY": "test_api_key"},
    )
    assert response.status_code == 200
    response_get = client.get(
        "/warehouses/" + test_data["id"], headers={"API_KEY": "test_api_key"}
    )
    assert response_get.status_code == 200
    assert response_get.json()["name"] == updated_warehouse["name"]


def test_delete_warehouse(client):
    response = client.delete(
        "/warehouses/" + test_data["id"], headers={"API_KEY": "test_api_key"}
    )
    assert response.status_code == 200
    time.sleep(1)
    response_get = client.get(
        "/warehouses/" + test_data["id"], headers={"API_KEY": "test_api_key"}
    )
    assert response_get.status_code == 200
    assert response_get.json() is None
