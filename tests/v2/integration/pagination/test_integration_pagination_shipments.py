import httpx
import pytest
from test_globals import *

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
        {"item_id": "P010669", "amount": 16},
        {"item_id": "P020333", "amount": 5},
        {"item_id": "P045782", "amount": 8},
    ],
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_shipments_page_1(client):
    response = client.get(f"/shipments{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipments_page_2(client):
    response = client.get(f"/shipments{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_shipments_page_0(client):
    response = client.get(f"/shipments{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipments_page_negative(client):
    response = client.get(f"/shipments{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipments_page_too_high(client):
    response_shipments = client.get("/shipments", headers=test_headers)
    assert response_shipments.status_code == 200
    response = client.get(
        f"/shipments{pagination_url_base}" + str(response_shipments.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipments_wrong_page_number(client):
    response = client.get("/shipments" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/shipments" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/shipments" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/shipments" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_shipment_orders_page_1(client):
    add_response = client.post("/shipments", json=test_shipment, headers=test_headers)
    assert add_response.status_code in [200, 201]
    test_shipment["id"] = add_response.json()["id"]
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_orders_page_0(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_orders_page_negative(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_orders_page_too_high(client):
    response_orders = client.get(
        f"/shipments/{test_shipment['id']}/orders", headers=test_headers
    )
    assert response_orders.status_code == 200
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders{pagination_url_base}"
        + str(response_orders.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_orders_wrong_page_number(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/orders" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422


def test_get_all_shipment_items_page_1(client):
    add_response = client.post("/shipments", json=test_shipment, headers=test_headers)
    assert add_response.status_code in [200, 201]
    test_shipment["id"] = add_response.json()["id"]
    response = client.get(
        f"/shipments/{test_shipment['id']}/items{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_items_page_0(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/items{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_items_page_negative(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_items_page_too_high(client):
    response_items = client.get(
        f"/shipments/{test_shipment['id']}/items", headers=test_headers
    )
    assert response_items.status_code == 200
    response = client.get(
        f"/shipments/{test_shipment['id']}/items{pagination_url_base}"
        + str(response_items.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_shipment_items_wrong_page_number(client):
    response = client.get(
        f"/shipments/{test_shipment['id']}/items" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/items" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/items" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/shipments/{test_shipment['id']}/items" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
