import httpx
import pytest
from test_globals import *


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_inventories_page_1(client):
    response = client.get(f"/inventories{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_inventories_page_2(client):
    response = client.get(f"/inventories{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_inventories_page_0(client):
    response = client.get(f"/inventories{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_inventories_page_negative(client):
    response = client.get(f"/inventories{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_inventories_page_too_high(client):
    response_inventories = client.get("/inventories/", headers=test_headers)
    assert response_inventories.status_code == 200
    response = client.get(
        "/inventories/page/"
        + str(response_inventories.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_inventories.json()["pagination"]["page"] == 1


def test_get_all_inventories_wrong_page_number(client):
    response = client.get("/inventories" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/inventories" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/inventories" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/inventories" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422
