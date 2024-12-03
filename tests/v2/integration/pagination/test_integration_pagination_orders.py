import pytest
import httpx
from test_globals import *

test_order = {
    "id": 99999999999999999,
    "source_id": 52,
    "order_date": "1983-09-26T19:06:08Z",
    "request_date": "1983-09-30T19:06:08Z",
    "reference": "ORD00003",
    "reference_extra": "Vergeven kamer goed enkele wiel tussen.",
    "order_status": "Delivered",
    "notes": "Zeil hoeveel onze map sex ding.",
    "shipping_notes": "Ontvangen schoon voorzichtig instrument ster vijver kunnen raam.",
    "picking_notes": "Grof geven politie suiker bodem zuid.",
    "warehouse_id": 11,
    "ship_to": None,
    "bill_to": None,
    "shipment_id": 3,
    "total_amount": 1156.14,
    "total_discount": 420.45,
    "total_tax": 677.42,
    "total_surcharge": 86.03,
    "created_at": "1983-09-26T19:06:08Z",
    "updated_at": "1983-09-28T15:06:08Z",
    "items": [
        {"item_id": "P010669", "amount": 16},
        {"item_id": "P010670", "amount": 17},
        {"item_id": "P010671", "amount": 18},
    ],
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_orders_page_1(client):
    response = client.get(f"/orders{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_orders_page_2(client):
    response = client.get(f"/orders{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_orders_page_0(client):
    response = client.get(f"/orders{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_orders_page_negative(client):
    response = client.get(f"/orders{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_orders_page_too_high(client):
    response_orders = client.get("/orders/", headers=test_headers)
    assert response_orders.status_code == 200
    response = client.get(
        "/orders/page/" + str(response_orders.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_orders.json()["pagination"]["page"] == 1


def test_get_all_orders_wrong_page_number(client):
    response = client.get("/orders" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/orders" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/orders" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/orders" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_order_items_page_1(client):
    add_order_response = client.post("/orders/", json=test_order, headers=test_headers)
    assert add_order_response.status_code in [200, 201]
    test_order["id"] = add_order_response.json()["id"]
    response = client.get(
        f"/orders/{test_order['id']}/items{pagination_url_1}", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_order_items_page_0(client):
    response = client.get(
        f"/orders/{test_order['id']}/items{pagination_url_0}", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_order_items_page_negative(client):
    response = client.get(
        f"/orders/{test_order['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_order_items_page_too_high(client):
    response_order_items = client.get(
        f"/orders/{test_order['id']}/items", headers=test_headers
    )
    assert response_order_items.status_code == 200
    response = client.get(
        f"/orders/{test_order['id']}/items/page/"
        + str(response_order_items.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_order_items.json()["pagination"]["page"] == 1


def test_get_all_order_items_wrong_page_number(client):
    response = client.get(
        f"/orders/{test_order['id']}/items" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/orders/{test_order['id']}/items" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/orders/{test_order['id']}/items" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/orders/{test_order['id']}/items" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
    response_delete_order = client.delete(
        f"/orders/{test_order['id']}", headers=test_headers
    )
    assert response_delete_order.status_code == 200
