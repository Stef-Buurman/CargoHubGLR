import pytest
import httpx
from test_globals import *

test_transfer = {
    "id": 99999999999999999,
    "reference": "TR00001",
    "transfer_from": None,
    "transfer_to": 9229,
    "transfer_status": "Completed",
    "created_at": "2000-03-11T13:11:14Z",
    "updated_at": "2000-03-12T16:11:14Z",
    "items": [{"item_id": "P007435", "amount": 23}],
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_transfers_page_1(client):
    response = client.get(f"/transfers{pagination_url_1}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfers_page_2(client):
    response = client.get(f"/transfers{pagination_url_2}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 2


def test_get_all_transfers_page_0(client):
    response = client.get(f"/transfers{pagination_url_0}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfers_page_negative(client):
    response = client.get(f"/transfers{pagination_url_negative}", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfers_page_too_high(client):
    response_transfers = client.get("/transfers/", headers=test_headers)
    assert response_transfers.status_code == 200
    response = client.get(
        "/transfers/page/" + str(response_transfers.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfers_wrong_page_number(client):
    response = client.get("/transfers" + wrong_page_1, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/transfers" + wrong_page_2, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/transfers" + wrong_page_3, headers=test_headers)
    assert response.status_code == 422
    response = client.get("/transfers" + wrong_page_4, headers=test_headers)
    assert response.status_code == 422


def test_get_all_transfer_items_page_1(client):
    add_transfer_response = client.post(
        "/transfers/", json=test_transfer, headers=test_headers
    )
    assert add_transfer_response.status_code in [200, 201]
    test_transfer["id"] = add_transfer_response.json()["id"]

    response = client.get(
        f"/transfers/{test_transfer['id']}/items{pagination_url_1}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfer_items_page_0(client):
    response = client.get(
        f"/transfers/{test_transfer['id']}/items{pagination_url_0}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfer_items_page_negative(client):
    response = client.get(
        f"/transfers/{test_transfer['id']}/items{pagination_url_negative}",
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfer_items_page_too_high(client):
    response_transfer_items = client.get(
        f"/transfers/{test_transfer['id']}/items", headers=test_headers
    )
    assert response_transfer_items.status_code == 200

    response = client.get(
        f"/transfers/{test_transfer['id']}/items/page/"
        + str(response_transfer_items.json()["pagination"]["pages"] + 1),
        headers=test_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["pagination"]["page"] == 1


def test_get_all_transfer_items_wrong_page_number(client):
    response = client.get(
        f"/transfers/{test_transfer['id']}/items" + wrong_page_1, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/transfers/{test_transfer['id']}/items" + wrong_page_2, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/transfers/{test_transfer['id']}/items" + wrong_page_3, headers=test_headers
    )
    assert response.status_code == 422
    response = client.get(
        f"/transfers/{test_transfer['id']}/items" + wrong_page_4, headers=test_headers
    )
    assert response.status_code == 422
    response_delete = client.delete(
        f"/transfers/{test_transfer['id']}", headers=test_headers
    )
    assert response_delete.status_code == 200
