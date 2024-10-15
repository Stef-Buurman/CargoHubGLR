import pytest
from fastapi.testclient import TestClient
from api.main import app

main_url = "http://localhost:3000/api/v1"


test_item = {
        "uid": "ditIsEenIdDieTochNooiZalGaanBestaan",
        "code": "oekiloekie",
        "description": "wat doet dit item",
        "short_description": "must",
        "upc_code": "6523540947122",
        "model_number": "63-OFFTq0T",
        "commodity_code": "oTo304",
        "item_line": 12,
        "item_group": 12,
        "item_type": 12,
        "unit_purchase_quantity": 47,
        "unit_order_quantity": 13,
        "pack_order_quantity": 11,
        "supplier_id": 34,
        "supplier_code": "SUP423",
        "supplier_part_number": "E-86805-uTM",
        "created_at": "2015-02-19 16:08:24",
        "updated_at": "2015-09-26 06:37:56"
    }

@pytest.fixture
def client():
    return TestClient(app)


def test_get_all_items(client):
    response = client.get('/items', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_item(client):
    response = client.post('/items', json=test_item, headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200

def test_get_item_by_id(client):
    response = client.get('/items/' + test_item['uid'], headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)

def test_get_nonexistent_item(client):
    response = client.get('/items/DitIsEenIdDieTochNooitBestaat', headers={"API_KEY": "test_api_key"})
    assert response.status_code == 404

def test_update_item(client):
    updated_item = test_item.copy()
    updated_item['code'] = 'updated_code'
    response = client.put('/items/' + test_item['uid'], json=updated_item, headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    response_get_item = client.get('/items/' + test_item['uid'], headers={"API_KEY": "test_api_key"})
    assert response_get_item.status_code == 200
    assert response_get_item.json()['code'] == updated_item['code']

def test_delete_item(client):
    response = client.delete('/items/' + test_item['uid'], headers={"API_KEY": "test_api_key"})
    assert response.status_code == 200
    response_get_item = client.get('/items/' + test_item['uid'], headers={"API_KEY": "test_api_key"})
    assert response_get_item.status_code == 404