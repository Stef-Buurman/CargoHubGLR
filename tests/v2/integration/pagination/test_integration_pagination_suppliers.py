import pytest
import httpx
from test_globals import *

test_supplier = {
    "id": 9999,
    "code": "SUP9999",
    "name": "Super coole test supplier",
    "address": "6942 Yoe Bide N.",
    "address_extra": "Apt. 420",
    "city": "Port Sigmaburgh",
    "zip_code": "42069",
    "province": "Illinois",
    "country": "Czech Republic",
    "contact_name": "Joe Biden",
    "phonenumber": "363.541.7282x36825",
    "reference": "LPaJ-SUP9999",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_suppliers_page_1(client):
    response = client.get(f"/suppliers{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_suppliers_page_2(client):
    response = client.get(f"/suppliers{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_suppliers_page_0(client):
    response = client.get(f"/suppliers{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_suppliers_page_negative(client):
    response = client.get(f"/suppliers{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_suppliers_page_too_high(client):
    response_suppliers = client.get("/suppliers", headers=test_headers)
    assert response_suppliers.status_code == 200
    response = client.get(
        f"/suppliers{pagination_url_base}"
        + str(response_suppliers.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_suppliers_wrong_page_number(client):
    response = client.get("/suppliers" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/suppliers" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/suppliers" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/suppliers" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_supplier_items_page_1(client):
    add_supplier_response = client.post(
        "/suppliers", json=test_supplier, headers=test_headers
    )
    assert add_supplier_response.status_code in [200, 201]
    test_supplier["id"] = add_supplier_response.json()["id"]
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_supplier_items_page_0(client):
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_supplier_items_page_negative(client):
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_supplier_items_page_too_high(client):
    response_supplier_items = client.get(
        f"/suppliers/{test_supplier['id']}/items", headers=test_headers
    )
    assert response_supplier_items.status_code == 200
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items{pagination_url_base}"
        + str(response_supplier_items.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_supplier_items_wrong_page_number(client):
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/suppliers/{test_supplier['id']}/items" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
    response_delete = client.delete(
        f"/suppliers/{test_supplier['id']}", headers=test_headers
    )
    assert response_delete.status_code == 200
