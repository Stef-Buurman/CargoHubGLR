import pytest
import httpx
from test_globals import *


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_locations_page_1(client):
    response = client.get(f"/locations{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_locations_page_2(client):
    response = client.get(f"/locations{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_locations_page_0(client):
    response = client.get(f"/locations{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_locations_page_negative(client):
    response = client.get(f"/locations{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_locations_page_too_high(client):
    response_locations = client.get("/locations/", headers=test_headers)
    assert response_locations.status_code == 200
    response = client.get(
        "/locations/page/" + str(response_locations.json()["pagination"]["page"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response_locations.json()["pagination"]["page"] == 1


def test_get_all_locations_wrong_page_number(client):
    response = client.get("/locations" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/locations" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/locations" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/locations" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422
