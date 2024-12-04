import pytest
import httpx
from test_globals import *


test_item = {
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
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_items_page_1(client):
    response = client.get(f"/items{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_items_page_2(client):
    response = client.get(f"/items{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_items_page_0(client):
    response = client.get(f"/items{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_items_page_negative(client):
    response = client.get(f"/items{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_items_page_too_high(client):
    response_items = client.get("/items/", headers=test_headers)
    assert response_items.status_code == 200
    response = client.get(
        "/items/page/" + str(response_items.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_items.json()["pagination"]["page"] == 1


def test_get_all_items_wrong_page_number(client):
    response = client.get("/items" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/items" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/items" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/items" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_item_inventories_page_1(client):
    response_add_item = client.post("/items/", headers=test_headers, json=test_item)
    assert response_add_item.status_code in [200, 201]
    test_item["uid"] = response_add_item.json()["uid"]
    response = client.get(
        f"/items/{test_item['uid']}/inventory{pagination_url_1}", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_inventories_page_0(client):
    response = client.get(
        f"/items/{test_item['uid']}/inventory{pagination_url_0}", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_inventories_page_negative(client):
    response = client.get(
        f"/items/{test_item['uid']}/inventory{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_inventories_page_too_high(client):
    response_item_inventories = client.get(
        f"/items/{test_item['uid']}/inventory", headers=test_headers
    )
    assert response_item_inventories.status_code == 200
    response = client.get(
        f"/items/{test_item['uid']}/inventory/page/"
        + str(response_item_inventories.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_item_inventories.json()["pagination"]["page"] == 1


def test_get_all_item_inventories_wrong_page_number(client):
    response = client.get(
        f"/items/{test_item['uid']}/inventory" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/items/{test_item['uid']}/inventory" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/items/{test_item['uid']}/inventory" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/items/{test_item['uid']}/inventory" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
    response_delete = client.delete(f"/items/{test_item['uid']}", headers=test_headers)
    assert response_delete.status_code == 200
