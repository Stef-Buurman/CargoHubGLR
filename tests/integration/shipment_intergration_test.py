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

test_shipment = {
    "id": 3,
    "order_id": 3,
    "source_id": 52,
    "order_date": "1973-01-28",
    "request_date": "1973-01-30",
    "shipment_date": "1973-02-01",
    "shipment_type": "I",
    "shipment_status": "Pending",
    "notes": "Hoog genot springen afspraak mond bus.",
    "carrier_code": "DHL",
    "carrier_description": "DHL Express",
    "service_code": "NextDay",
    "payment_type": "Automatic",
    "transfer_mode": "Ground",
    "total_package_count": 29,
    "total_package_weight": 463.0,
    "created_at": "1973-01-28T20:09:11Z",
    "updated_at": "1973-01-29T22:09:11Z",
    "items": [
        {
            "item_id": "P010669",
            "amount": 16
        },
        {
            "item_id": "P020333",
            "amount": 5
        },
        {
            "item_id": "P045782",
            "amount": 8
        }
    ]
}

@pytest.fixture
def client():
    with httpx.Client(base_url=main_url) as client:
        yield client

def test_get_all_shipments(client):
    response = client.get('/shipments', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_shipment(client):
    response = client.post('/shipments', json=test_shipment, headers={"API_KEY": "test_api_key"})
    assert response.status_code == 201

def test_get_shipment_by_id(client):
    response = client.get(f'/shipments/{test_shipment["id"]}', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)

def test_get_nonexistent_shipment(client):
    response = client.get('/shipments/9999999', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 404

def test_update_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put(f'/shipments/{test_shipment["id"]}', json=updated_shipment, headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    response_get_shipment = client.get(f'/shipments/{test_shipment["id"]}', headers={"API_KEY": "test_api_key"})
    assert response_get_shipment.status_code == 200
    assert response_get_shipment.json()['shipment_status'] == 'Shipped'

def test_delete_shipment(client):
    response = client.delete(f'/shipments/{test_shipment["id"]}', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    time.sleep(1)
    response_get_shipment = client.get(f'/shipments/{test_shipment["id"]}', headers={"API_KEY": "test_api_key"})
    assert response_get_shipment.status_code == 404
    assert response_get_shipment.json() is None