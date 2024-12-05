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
test_item = {
    "code": "oekiloekie",
    "description": "wat doet dit item",
    "short_description": "must",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 12,
    "item_group": test_item_group["id"],
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


def test_get_all_item_groups(client):
    response = client.get("/item_groups/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


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
    test_item_group["id"] = response.json()["id"]
    test_item["item_group"] = response.json()["id"]


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


def test_get_items_for_item_group_non_existing_id(client):
    response = client.get(
        "/item_groups/" + str(non_existent_id) + "/items", headers=test_headers
    )
    assert response.status_code == 404


def test_get_items_for_item_group(client):
    responseAddItem = client.post("/items/", json=test_item, headers=test_headers)
    assert responseAddItem.status_code == 201 or responseAddItem.status_code == 200
    response = client.get(
        "/item_groups/" + str(test_item_group["id"]) + "/items", headers=test_headers
    )
    response_items = response.json()["data"]
    assert response.status_code == 200
    assert isinstance(response_items, list)
    assert response_items[0]["uid"] == responseAddItem.json()["uid"]
    responseDeleteItem = client.delete(
        "/items/" + response_items[0]["uid"], headers=test_headers
    )
    assert responseDeleteItem.status_code == 200


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


def test_partial_update_item_group_no_api_key(client):
    updated_item_group = {"name": "Updated Inc"}
    response = client.patch(
        f"/item_groups/{test_item_group['id']}", json=updated_item_group
    )
    assert response.status_code == 403


def test_partial_update_item_group_invalid_api_key(client):
    updated_item_group = {"name": "Updated Inc"}
    response = client.patch(
        f"/item_groups/{test_item_group['id']}",
        json=updated_item_group,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_invalid_item_group_id(client):
    updated_item_group = {"name": "Updated Inc"}
    response = client.patch(
        "/item_groups/invalid_id", json=updated_item_group, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_nonexistent_item_group(client):
    updated_item_group = {"name": "Updated Inc"}
    response = client.patch(
        f"/item_groups/{non_existent_id}", json=updated_item_group, headers=test_headers
    )
    assert response.status_code == 404


def test_partial_update_item_group(client):
    updated_item_group = {"name": "Updated Inc"}
    response = client.patch(
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


def test_archive_item_group_no_api_key(client):
    response = client.delete("/item_groups/" + str(test_item_group["id"]))
    assert response.status_code == 403
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 200


def test_archive_item_group_invalid_api_key(client):
    response = client.delete(
        "/item_groups/" + str(test_item_group["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 200


def test_archive_item_group_invalid_id(client):
    response = client.delete("/item_groups/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_archive_nonexistent_item_group(client):
    response = client.delete(
        "/item_groups/" + str(non_existent_id), headers=test_headers
    )
    assert response.status_code == 404


def test_archive_item_group(client):
    response = client.delete(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_item_group = client.get(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response_get_item_group.status_code == 404


def test_archive_item_group_already_archived(client):
    response = client.delete(
        "/item_groups/" + str(test_item_group["id"]), headers=test_headers
    )
    assert response.status_code == 400


def test_unarchive_item_group_no_api_key(client):
    response = client.patch(f"/item_groups/{test_item_group['id']}/unarchive")
    assert response.status_code == 403
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 404


def test_unarchive_item_group_invalid_api_key(client):
    response = client.patch(
        f"/item_groups/{test_item_group['id']}/unarchive", headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 404


def test_unarchive_item_group_invalid_id(client):
    response = client.patch("/item_groups/invalid_id/unarchive", headers=test_headers)
    assert response.status_code == 422


def test_unarchive_nonexistent_item_group(client):
    response = client.patch(
        f"/item_groups/{non_existent_id}/unarchive", headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_item_group(client):
    response = client.patch(
        f"/item_groups/{test_item_group['id']}/unarchive", headers=test_headers
    )
    assert response.status_code == 200
    response_get_item_group = client.get(
        f"/item_groups/{test_item_group['id']}", headers=test_headers
    )
    assert response_get_item_group.status_code == 200
    assert response_get_item_group.json()["is_archived"] is False


def test_unarchive_item_group_not_archived(client):
    response = client.patch(
        f"/item_groups/{test_item_group['id']}/unarchive", headers=test_headers
    )
    assert response.status_code == 400