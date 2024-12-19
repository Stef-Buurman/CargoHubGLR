import httpx
import pytest
from test_globals import *

test_item_group = {
    "id": 999999999,
    "name": "Electronics",
    "description": "",
    "created_at": "1998-05-15 19:52:53",
    "updated_at": "2000-11-20 08:37:56",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_item_groups_page_1(client):
    response = client.get(f"/item_groups{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_groups_page_2(client):
    response = client.get(f"/item_groups{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_item_groups_page_0(client):
    response = client.get(f"/item_groups{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_groups_page_negative(client):
    response = client.get(
        f"/item_groups{pagination_url_negative}", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_groups_page_too_high(client):
    response_item_groups = client.get("/item_groups", headers=test_headers)
    assert response_item_groups.status_code == 200
    response = client.get(
        f"/item_groups{pagination_url_base}"
        + str(response_item_groups.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_groups_wrong_page_number(client):
    response = client.get("/item_groups" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_groups" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_groups" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/item_groups" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_item_groups_items_page_1(client):
    response_add_item_group = client.post(
        f"/item_groups", json=test_item_group, headers=test_headers
    )
    assert response_add_item_group.status_code in [200, 201]
    test_item_group["id"] = response_add_item_group.json()["id"]
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_group_items_page_0(client):
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_group_items_page_negative(client):
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_group_items_page_too_high(client):
    response_items = client.get(
        f"/item_groups/{test_item_group['id']}/items", headers=test_headers
    )
    assert response_items.status_code == 200
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items{pagination_url_base}{response_items.json()['pagination']['pages'] + 1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_item_group_items_wrong_page_number(client):
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items" + wrong_page_1,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items" + wrong_page_2,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items" + wrong_page_3,
        headers=test_headers,
    )
    assert response.status_code == 422
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items" + wrong_page_4,
        headers=test_headers,
    )
    assert response.status_code == 422
    response_delete = client.delete(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_delete.status_code == 200
