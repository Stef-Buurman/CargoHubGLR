import httpx
import pytest
from test_globals import MAIN_URL

test_headers = {"API_KEY": "test_api_key"}
invalid_headers={"API_KEY": "invalid_key"}
never_existing_id = "99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999"

test_shipment = {
    "id": 999999999,
    "order_id": 900,
    "source_id": 900,
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
    with httpx.Client(base_url=MAIN_URL) as client:
        yield client


def test_get_all_shipments(client):
    response = client.get('/shipments/', headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_shipments_no_api_key(client):
    response = client.get('/shipments/')
    assert response.status_code == 403


def test_get_all_shipments_invalid_api_key(client):
    response = client.get('/shipments/', headers=invalid_headers)
    assert response.status_code == 403


def test_add_shipment_no_api_key(client):
    response = client.post('/shipments/', json=test_shipment)
    assert response.status_code == 403
    responseGet = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert responseGet.status_code == 404


def test_add_shipment_invalid_api_key(client):
    response = client.post('/shipments/', json=test_shipment, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert responseGet.status_code == 404

def test_add_shipment(client):
    response = client.post('/shipments/', json=test_shipment, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    assert response.json()["id"] == test_shipment["id"]
    
def test_add_existing_shipment(client):
    response = client.post('/shipments/', json=test_shipment, headers=test_headers)
    assert response.status_code == 409


def test_get_shipment_by_id(client):
    response = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()['id'] == test_shipment['id']


def test_get_shipment_no_api_key(client):
    response = client.get('/shipments/' + str(test_shipment['id']))
    assert response.status_code == 403 


def test_get_shipment_invalid_api_key(client):
    response = client.get('/shipments/' + str(test_shipment['id']), headers=invalid_headers)
    assert response.status_code == 403 


def test_get_invalid_shipment_id(client):
    response = client.get('/shipments/invalid_id', headers=test_headers)
    assert response.status_code == 422


def test_get_nonexistent_shipment(client):
    response = client.get('/shipments/'+never_existing_id, headers=test_headers)
    assert response.status_code == 404


def test_update_shipment_no_api_key(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put('/shipments/' + str(test_shipment['id']), json=updated_shipment)
    assert response.status_code == 403
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 200
    assert response_get_shipment.json()['shipment_status'] == test_shipment['shipment_status']


def test_update_shipment_invalid_api_key(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put('/shipments/' + str(test_shipment['id']), json=updated_shipment, headers=invalid_headers)
    assert response.status_code == 403
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 200
    assert response_get_shipment.json()['shipment_status'] == test_shipment['shipment_status']


def test_update_invalid_shipment_id(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put('/shipments/invalid_id', json=updated_shipment, headers=test_headers)
    assert response.status_code == 422


def test_update_nonexistent_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put('/shipments/'+never_existing_id, json=updated_shipment, headers=test_headers)
    assert response.status_code == 404


def test_update_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment['shipment_status'] = 'Shipped'
    response = client.put('/shipments/' + str(test_shipment['id']), json=updated_shipment, headers=test_headers)
    assert response.status_code == 200
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 200
    assert response_get_shipment.json()['shipment_status'] == updated_shipment['shipment_status']


def test_delete_shipment_no_api_key(client):
    response = client.delete('/shipments/' + str(test_shipment['id']))
    assert response.status_code == 403
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 200


def test_delete_shipment_invalid_api_key(client):
    response = client.delete('/shipments/' + str(test_shipment['id']), headers=invalid_headers)
    assert response.status_code == 403
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 200


def test_delete_shipment(client):
    response = client.delete('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response.status_code == 200
    response_get_shipment = client.get('/shipments/' + str(test_shipment['id']), headers=test_headers)
    assert response_get_shipment.status_code == 404
