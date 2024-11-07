import pytest
import httpx
from tests.integration.test_globals import *


test_item = {
    "code": "oekiloekie",
    "description": "wat doet dit item",
    "short_description": "must",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 12,
    "item_group": 12,
    "item_type": 12,
    "unit_purchase_quantity": 47,
    "unit_order_quantity": 13,
    "pack_order_quantity": 11,
    "supplier_id": 34,
    "supplier_code": "SUP423",
    "supplier_part_number": "E-86805-uTM",
}

test_inventory = {
    "id": 99999999999999999,
    "description": "Multi-layered intangible artificial intelligence",
    "item_reference": "aro81493o",
    "locations": [27132, 11010, 10381, 34058, 31838, 21993, 9540],
    "total_on_hand": 159,
    "total_expected": 0,
    "total_ordered": 91,
    "total_allocated": 5,
    "total_available": 63,
    "created_at": "1986-10-17 07:19:42",
    "updated_at": "1989-03-30 17:53:04",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2) as client:
        yield client


def test_get_all_items(client):
    response = client.get("/items/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_items_no_api_key(client):
    response = client.get("/items/")
    assert response.status_code == 403


def test_get_all_items_invalid_api_key(client):
    response = client.get("/items/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_item_no_api_key(client):
    response = client.post("/items/", json=test_item)
    assert response.status_code == 403


def test_add_item_invalid_api_key(client):
    response = client.post("/items/", json=test_item, headers=invalid_headers)
    assert response.status_code == 403


def test_add_item(client):
    response = client.post("/items/", json=test_item, headers=test_headers)
    assert response.status_code == 201
    test_item["uid"] = response.json()["uid"]
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200
    assert response_get_item.json()["uid"] == test_item["uid"]


# def test_add_existing_item(client):
#     response = client.post("/items/", json=test_item, headers=test_headers)
#     assert response.status_code == 409


def test_get_item_no_api_key(client):
    response = client.get("/items/" + test_item["uid"])
    assert response.status_code == 403


def test_get_item_invalid_api_key(client):
    response = client.get("/items/" + test_item["uid"], headers=invalid_headers)
    assert response.status_code == 403


def test_get_item_by_id(client):
    response = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)


def test_get_nonexistent_item(client):
    response = client.get("/items/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_inventory_of_item_no_api_key(client):
    response = client.get("/items/" + test_item["uid"] + "/inventory")
    assert response.status_code == 403


def test_get_inventory_of_item_invalid_api_key(client):
    response = client.get(
        "/items/" + test_item["uid"] + "/inventory", headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_inventory_of_nonexistent_item(client):
    response = client.get(
        "/items/" + str(non_existent_id) + "/inventory", headers=test_headers
    )
    assert response.status_code == 404


def test_get_inventory_of_item(client):
    test_inventory["item_id"] = test_item["uid"]
    responseAddInventory = client.post(
        "/inventories/", json=test_inventory, headers=test_headers
    )
    assert (
        responseAddInventory.status_code == 201
        or responseAddInventory.status_code == 200
    )
    response = client.get(
        "/items/" + test_item["uid"] + "/inventory", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["item_id"] == test_item["uid"]


def test_get_inventory_totals_of_item_no_api_key(client):
    response = client.get("/items/" + test_item["uid"] + "/inventory/totals")
    assert response.status_code == 403


def test_get_inventory_totals_of_item_invalid_api_key(client):
    response = client.get(
        "/items/" + test_item["uid"] + "/inventory/totals", headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_inventory_totals_of_nonexistent_item(client):
    response = client.get(
        "/items/" + str(non_existent_id) + "/inventory/totals", headers=test_headers
    )
    assert response.status_code == 404


def test_get_inventory_totals_of_item(client):
    response = client.get(
        "/items/" + test_item["uid"] + "/inventory/totals", headers=test_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["total_expected"] == test_inventory["total_expected"]
    assert response.json()["total_ordered"] == test_inventory["total_ordered"]
    assert response.json()["total_allocated"] == test_inventory["total_allocated"]
    assert response.json()["total_available"] == test_inventory["total_available"]
    responseDeleteInventory = client.delete(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert responseDeleteInventory.status_code == 200
    responseGetInventory = client.get(
        "/inventories/" + str(test_inventory["id"]), headers=test_headers
    )
    assert responseGetInventory.status_code == 404


def test_update_item_no_api_key(client):
    updated_item = test_item.copy()
    updated_item["code"] = "updated_code"
    response = client.put("/items/" + test_item["uid"], json=updated_item)
    assert response.status_code == 403
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200
    assert response_get_item.json()["code"] == test_item["code"]


def test_update_item_invalid_api_key(client):
    updated_item = test_item.copy()
    updated_item["code"] = "updated_code"
    response = client.put(
        "/items/" + test_item["uid"], json=updated_item, headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200
    assert response_get_item.json()["code"] == test_item["code"]


def test_update_item_no_item(client):
    updated_item = test_item.copy()
    updated_item["code"] = "updated_code"
    response = client.put(
        "/items/" + str(non_existent_id), json=updated_item, headers=test_headers
    )
    assert response.status_code == 404


def test_update_item(client):
    updated_item = test_item.copy()
    updated_item["code"] = "updated_code"
    response = client.put(
        "/items/" + test_item["uid"], json=updated_item, headers=test_headers
    )
    assert response.status_code == 200
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200
    assert response_get_item.json()["code"] == updated_item["code"]


def test_delete_item_no_api_key(client):
    response = client.delete("/items/" + test_item["uid"])
    assert response.status_code == 403
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200


def test_delete_item_invalid_api_key(client):
    response = client.delete("/items/" + test_item["uid"], headers=invalid_headers)
    assert response.status_code == 403
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200


def test_delete_item_no_item(client):
    response = client.delete("/items/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 200


def test_delete_item(client):
    response = client.delete("/items/" + test_item["uid"], headers=test_headers)
    assert response.status_code == 200
    response_get_item = client.get("/items/" + test_item["uid"], headers=test_headers)
    assert response_get_item.status_code == 404
