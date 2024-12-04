import pytest
import httpx
from test_globals import *

test_warehouse = {
    "id": 99999999999999999,
    "code": "YQZZNL56",
    "name": "Heemskerk cargo hub",
    "address": "Karlijndreef 281",
    "zip": "4002 AS",
    "city": "Heemskerk",
    "province": "Friesland",
    "country": "NL",
    "contact_name": "Fem Keijzer",
    "contact_phone": "(078) 0013363",
    "contact_email": "blamore@example.net",
    "created_at": "1983-04-13 04:59:55",
    "updated_at": "2007-02-08 20:11:00",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_warehouses_page_1(client):
    response = client.get(f"/warehouses{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouses_page_2(client):
    response = client.get(f"/warehouses{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_warehouses_page_0(client):
    response = client.get(f"/warehouses{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouses_page_negative(client):
    response = client.get(f"/warehouses{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouses_page_too_high(client):
    response_warehouses = client.get("/warehouses/", headers=test_headers)
    assert response_warehouses.status_code == 200
    response = client.get(
        "/warehouses/page/" + str(response_warehouses.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouses_wrong_page_number(client):
    response = client.get("/warehouses" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/warehouses" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/warehouses" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/warehouses" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_warehouse_locations_page_1(client):
    add_response = client.post(
        "/warehouses/", headers=test_headers, json=test_warehouse
    )
    assert add_response.status_code in [200, 201]
    test_warehouse["id"] = add_response.json()["id"]
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouse_locations_page_0(client):
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouse_locations_page_negative(client):
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouse_locations_page_too_high(client):
    response_warehouse_locations = client.get(
        f"/warehouses/{test_warehouse['id']}/locations", headers=test_headers
    )
    assert response_warehouse_locations.status_code == 200
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations/page/"
        + str(response_warehouse_locations.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_warehouse_locations_wrong_page_number(client):
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations" + wrong_page_1,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations" + wrong_page_2,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations" + wrong_page_3,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/warehouses/{test_warehouse['id']}/locations" + wrong_page_4,
        headers=test_headers,
    )
    assert response.status_code == 422
    response_delete = client.delete(
        f"/warehouses/{test_warehouse['id']}", headers=test_headers
    )
    assert response_delete.status_code == 200
