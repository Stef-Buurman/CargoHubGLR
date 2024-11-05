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
    with httpx.Client(base_url=MAIN_URL) as client:
        yield client


def test_get_all_item_groups(client):
    response = client.get("/item_groups/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_item_groups_no_api_key(client):
    response = client.get("/item_groups/")
    assert response.status_code == 403


def test_get_all_item_groups_invalid_api_key(client):
    response = client.get("/item_groups/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_item_group_no_api_key(client):
    response = client.post("/item_groups/", json=test_item_group)
    assert response.status_code == 403
    responseGet = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_item_group_invalid_api_key(client):
    response = client.post(
        "/item_groups/", json=test_item_group, headers=invalid_headers
    )
    assert response.status_code == 403
    responseGet = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_item_group(client):
    response = client.post("/item_groups/", json=test_item_group, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    assert response.json()["id"] == test_item_group["id"]


def test_add_existing_item_group(client):
    response = client.post("/item_groups/", json=test_item_group, headers=test_headers)
    assert response.status_code == 409


def test_get_item_group_by_id(client):
    response = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_item_group["id"]


def test_get_item_group_no_api_key(client):
    response = client.get("/item_groups/" + str(test_item_group["id"]))
    assert response.status_code == 403


def test_get_item_group_invalid_api_key(client):
    response = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_invalid_item_group_id(client):
    response = client.get("/item_groups/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_get_nonexistent_item_group(client):
    response = client.get("/item_groups/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_items_for_item_group(client):
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items", headers=test_headers
    )
    assert response.status_code == 200


def test_get_items_for_nonexistent_item_group(client):
    response = client.get(f"/item_groups/{non_existent_id}/items", headers=test_headers)
    assert response.status_code == 404


def test_get_items_for_invalid_item_group_id(client):
    response = client.get("/item_groups/invalid_id/items", headers=test_headers)
    assert response.status_code == 422


def test_get_items_for_item_group_no_api_key(client):
    response = client.get(f"/item_groups/{test_item_group['id']}/items")
    assert response.status_code == 403


def test_get_items_for_item_group_invalid_api_key(client):
    response = client.get(
        f"/item_groups/{test_item_group['id']}/items", headers=invalid_headers
    )
    assert response.status_code == 403


def test_update_item_group_no_api_key(client):
    updated_item_group = test_item_group.copy()
    updated_item_group["name"] = "Updated Inc"
    response = client.put(
        f"/item_groups/{test_item_group['id']}", json=updated_item_group
    )
    assert response.status_code == 403
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 200
    assert response_get_item_group.json()["name"] == test_item_group["name"]


def test_update_item_group_invalid_api_key(client):
    updated_item_group = test_item_group.copy()
    updated_item_group["name"] = "Updated Inc"
    response = client.put(
        f"/item_groups/{test_item_group['id']}",
        json=updated_item_group,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 200
    assert response_get_item_group.json()["name"] == test_item_group["name"]


def test_update_invalid_item_group_id(client):
    updated_item_group = test_item_group.copy()
    updated_item_group["name"] = "Updated Inc"
    response = client.put(
        "/item_groups/invalid_id", json=updated_item_group, headers=test_headers
    )
    assert response.status_code == 422


def test_update_nonexistent_item_group(client):
    updated_item_group = test_item_group.copy()
    updated_item_group["name"] = "Updated Inc"
    response = client.put(
        f"/item_groups/{non_existent_id}", json=updated_item_group, headers=test_headers
    )
    assert response.status_code == 404


def test_update_item_group(client):
    updated_item_group = test_item_group.copy()
    updated_item_group["name"] = "Updated Inc"
    response = client.put(
        f"/item_groups/{test_item_group['id']}",
        json=updated_item_group,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 200
    assert response_get_item_group.json()["name"] == updated_item_group["name"]


def test_delete_item_group_no_api_key(client):
    response = client.delete("/item_groups/" + str(test_item_group["id"]))
    assert response.status_code == 403
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 200


def test_delete_item_group_invalid_api_key(client):
    response = client.delete(
        "/item_groups/" + str(test_item_group["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 200


def test_delete_item_group(client):
    response = client.delete(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 404
