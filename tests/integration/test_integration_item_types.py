import httpx
import pytest
from test_globals import *


test_item_type =     {
        "id": 9009098098908779890978162356712312736871219,
        "name": "Dit is een hele mooie test naam!",
        "description": "",
        "created_at": "2023-03-16 11:54:38",
        "updated_at": "2023-12-02 07:01:00"
    }


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL) as client:
        yield client


def test_get_all_item_types(client):
    response = client.get('/item_types/', headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_item_types_no_api_key(client):
    response = client.get('/item_types/')
    assert response.status_code == 403


def test_get_all_item_types_invalid_api_key(client):
    response = client.get('/item_types/', headers=invalid_headers)
    assert response.status_code == 403


def test_add_item_type_no_api_key(client):
    response = client.post('/item_types/', json=test_item_type)
    assert response.status_code == 403
    responseGet = client.get('/item_types/' + str(test_item_type['id']), headers=test_headers)
    assert responseGet.status_code == 404


def test_add_item_type_invalid_api_key(client):
    response = client.post('/item_types/', json=test_item_type, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get('/item_types/' + str(test_item_type['id']), headers=test_headers)
    assert responseGet.status_code == 404


def test_add_item_type(client):
    response = client.post('/item_types/', json=test_item_type, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    responseGet = client.get('/item_types/' + str(test_item_type['id']), headers=test_headers)
    assert responseGet.status_code == 200
    assert response.json()["id"] == test_item_type["id"]


def test_add_existing_item_type(client):
    response = client.post('/item_types/', json=test_item_type, headers=test_headers)
    assert response.status_code == 409


def test_get_item_type_by_id(client):
    response = client.get('/item_types/' + str(test_item_type['id']), headers=test_headers)
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)


def test_get_item_type_no_api_key(client):
    response = client.get('/item_types/' + str(test_item_type['id']))
    assert response.status_code == 403


def test_get_item_type_invalid_api_key(client):
    response = client.get('/item_types/' + str(test_item_type['id']), headers=invalid_headers)
    assert response.status_code == 403


def test_get_items_for_item_type_without_items(client):
    response = client.get('/item_types/' + str(test_item_type['id']) + '/items', headers=test_headers)
    assert response.status_code == 204


def test_get_items_for_item_type(client):
    response = client.get('/item_types/' + str(non_existent_id) + '/items', headers=invalid_headers)
    assert response.status_code == 404


def test_get_items_for_item_type_no_api_key(client):
    response = client.get('/item_types/' + str(test_item_type['id']) + '/items')
    assert response.status_code == 403


def test_get_items_for_item_type_invalid_api_key(client):
    response = client.get('/item_types/' + str(test_item_type['id']) + '/items', headers=invalid_headers)
    assert response.status_code == 403


def test_get_items_for_item_type_not_found(client):
    response = client.get('/item_types/' + str(non_existent_id) + '/items', headers=invalid_headers)
    assert response.status_code == 404


def test_update_item_type(client):
    response = client.put('/item_types/' + str(test_item_type['id']), json=test_item_type, headers=test_headers)
    assert response.status_code == 200
    responseGet = client.get('/item_types/' + str(test_item_type['id']), headers=test_headers)
    assert responseGet.status_code == 200
    assert response.json()["id"] == test_item_type["id"]