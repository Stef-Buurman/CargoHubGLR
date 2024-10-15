import pytest
from fastapi.testclient import TestClient
from api.main import app

test_headers = {"API_KEY": "test_api_key"}

test_inventory = {
        "id": 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999,
        "code": "YQZZNL56",
        "name": "Delft Warehouse",
        "address": "HermanStraat 12",
        "zip": "4002 AS",
        "city": "Delft",
        "province": "Zuid-Holland",
        "country": "NL",
        "contact": {
            "name": "Fem Keijzer",
            "phone": "(078) 0013363",
            "email": "blamore@example.net"
        },
        "created_at": "1983-04-13 04:59:55",
        "updated_at": "2007-02-08 20:11:00"
    }

@pytest.fixture
def client():
    return TestClient(app)

def test_get_all_items(client):
    response = client.get('/items', headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_item(client):
    response = client.post('/items', json=test_inventory, headers=test_headers)
    assert response.status_code == 200
    responseGetAddedItem = client.get('/items/' + test_inventory['id'], headers=test_headers)
    assert responseGetAddedItem.status_code == 200
    assert responseGetAddedItem.json() is not None
