import httpx
import pytest
from test_globals import *

test_item_type = {
    "id": 99999999999999999,
    "name": "Dit is een hele mooie test naam!",
    "description": "",
    "created_at": "2023-03-16 11:54:38",
    "updated_at": "2023-12-02 07:01:00",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_item_types_page_1(client):
    response = client.get(f"/item_types{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_page_2(client):
    response = client.get(f"/item_types{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_item_types_page_0(client):
    response = client.get(f"/item_types{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_page_negative(client):
    response = client.get(f"/item_types{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_page_too_high(client):
    response_item_types = client.get("/item_types", headers=test_headers)
    assert response_item_types.status_code == 200
    response = client.get(
        "/item_types/page"
        + str(response_item_types.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_wrong_page_number(client):
    response = client.get("/item_types" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_types" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_types" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_types" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_item_types_items_page_1(client):
    response_add_item_type = client.post(
        "/item_types", headers=test_headers, json=test_item_type
    )
    assert response_add_item_type.status_code in [200, 201]
    test_item_type["id"] = response_add_item_type.json()["id"]
    response = client.get(
        f"/item_types/{test_item_type['id']}/items{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_items_page_0(client):
    response = client.get(
        f"/item_types/{test_item_type['id']}/items{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_items_page_negative(client):
    response = client.get(
        f"/item_types/{test_item_type['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_items_page_too_high(client):
    response_item_types = client.get(
        f"/item_types/{test_item_type['id']}/items", headers=test_headers
    )
    assert response_item_types.status_code == 200
    response = client.get(
        f"/item_types/{test_item_type['id']}/items/page"
        + str(response_item_types.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_types_items_wrong_page_number(client):
    response = client.get(
        f"/item_types/{test_item_type['id']}/items" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_types/{test_item_type['id']}/items" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_types/{test_item_type['id']}/items" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_types/{test_item_type['id']}/items" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
    response_delete = client.delete(
        f"/item_types/{test_item_type['id']}", headers=test_headers
    )
    assert response_delete.status_code == 200
