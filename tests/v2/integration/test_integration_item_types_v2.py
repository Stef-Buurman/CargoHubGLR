import httpx
import pytest
from test_globals import *


test_item_type = {
    "id": 99999999999999999,
    "name": "Dit is een hele mooie test naam!",
    "description": "",
    "created_at": "2023-03-16 11:54:38",
    "updated_at": "2023-12-02 07:01:00",
}

test_item = {
    "code": "oekiloekie",
    "description": "wat doet dit item",
    "short_description": "must",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 12,
    "item_group": 12,
    "item_type": test_item_type["id"],
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


# def test_get_all_item_types(client):
#     response = client.get("/item_types/", headers=test_headers)
#     assert response.status_code == 200
#     assert isinstance(response.json()["data"], list)


# def test_get_all_item_types_no_api_key(client):
#     response = client.get("/item_types/")
#     assert response.status_code == 403


# def test_get_all_item_types_invalid_api_key(client):
#     response = client.get("/item_types/", headers=invalid_headers)
#     assert response.status_code == 403


# def test_add_item_type_no_api_key(client):
#     response = client.post("/item_types/", json=test_item_type)
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 404


# def test_add_item_type_invalid_api_key(client):
#     response = client.post("/item_types/", json=test_item_type, headers=invalid_headers)
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 404


def test_add_item_type(client):
    response = client.post("/item_types/", json=test_item_type, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_item_type["id"] = response.json()["id"]
    test_item["item_type"] = response.json()["id"]
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200


# def test_get_item_type_by_id(client):
#     response = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert response.status_code == 200
#     assert response.json() is not None
#     assert isinstance(response.json(), dict)


# def test_get_item_type_no_api_key(client):
#     response = client.get("/item_types/" + str(test_item_type["id"]))
#     assert response.status_code == 403


# def test_get_item_type_invalid_api_key(client):
#     response = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_get_item_type_not_found(client):
#     response = client.get("/item_types/" + str(non_existent_id), headers=test_headers)
#     assert response.status_code == 404


# def test_get_item_type_invalid_id(client):
#     response = client.get("/item_types/invalidId", headers=test_headers)
#     assert response.status_code == 422


# def test_get_items_for_item_type_no_api_key(client):
#     response = client.get("/item_types/" + str(test_item_type["id"]) + "/items")
#     assert response.status_code == 403


# def test_get_items_for_item_type_invalid_api_key(client):
#     response = client.get(
#         "/item_types/" + str(test_item_type["id"]) + "/items", headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_get_items_for_item_type(client):
#     responseAddItem = client.post("/items/", json=test_item, headers=test_headers)
#     assert responseAddItem.status_code == 201 or responseAddItem.status_code == 200
#     response = client.get(
#         "/item_types/" + str(test_item_type["id"]) + "/items", headers=test_headers
#     )
#     response_items = response.json()["data"]
#     assert response.status_code == 200
#     assert isinstance(response_items, list)
#     assert response_items[0]["uid"] == responseAddItem.json()["uid"]
#     responseDeleteItem = client.delete(
#         "/items/" + responseAddItem.json()["uid"], headers=test_headers
#     )
#     assert responseDeleteItem.status_code == 200


# def test_get_items_for_item_type_not_found(client):
#     response = client.get(
#         "/item_types/" + str(non_existent_id) + "/items", headers=test_headers
#     )
#     assert response.status_code == 404


# def test_get_items_for_item_type_invalid_id(client):
#     response = client.get("/item_types/invalidId/items", headers=test_headers)
#     assert response.status_code == 422


# def test_update_item_type_no_api_key(client):
#     test_item_type_copy = test_item_type.copy()
#     test_item_type_copy["name"] = "Updated Inc"
#     response = client.put(
#         "/item_types/" + str(test_item_type["id"]), json=test_item_type_copy
#     )
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["name"] == test_item_type["name"]


# def test_update_item_type_invalid_api_key(client):
#     test_item_type_copy = test_item_type.copy()
#     test_item_type_copy["name"] = "Updated Inc"
#     response = client.put(
#         "/item_types/" + str(test_item_type["id"]),
#         json=test_item_type_copy,
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["name"] == test_item_type["name"]


# def test_update_item_type_invalid_id(client):
#     test_item_type_copy = test_item_type.copy()
#     test_item_type_copy["name"] = "Updated Inc"
#     response = client.put(
#         "/item_types/invalidId", json=test_item_type_copy, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_update_item_type_not_found(client):
#     test_item_type_copy = test_item_type.copy()
#     test_item_type_copy["name"] = "Updated Inc"
#     response = client.put(
#         "/item_types/" + str(non_existent_id),
#         json=test_item_type_copy,
#         headers=test_headers,
#     )
#     assert response.status_code == 404


# def test_update_item_type(client):
#     test_item_type_copy = test_item_type.copy()
#     test_item_type_copy["name"] = "Updated Inc"
#     response = client.put(
#         "/item_types/" + str(test_item_type["id"]),
#         json=test_item_type_copy,
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json()["name"] == test_item_type_copy["name"]
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["name"] == test_item_type_copy["name"]


# def test_partial_update_item_type_no_api_key(client):
#     updated_item_type = {"name": "Super coole nieuwe naam voor de test item_type"}
#     response = client.patch(
#         "/item_types/" + str(test_item_type["id"]), json=updated_item_type
#     )
#     assert response.status_code == 403


# def test_partial_update_item_type_invalid_api_key(client):
#     updated_item_type = {"name": "Super coole nieuwe naam voor de test item_type"}
#     response = client.patch(
#         "/item_types/" + str(test_item_type["id"]),
#         json=updated_item_type,
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403


# def test_partial_update_item_type_invalid_id(client):
#     updated_item_type = {"name": "Super coole nieuwe naam voor de test item_type"}
#     response = client.patch(
#         "/item_types/invalid_id", json=updated_item_type, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_partial_update_item_type_non_existent_id(client):
#     updated_item_type = {"name": "Super coole nieuwe naam voor de test item_type"}
#     response = client.patch(
#         "/item_types/" + str(non_existent_id),
#         json=updated_item_type,
#         headers=test_headers,
#     )
#     assert response.status_code == 404


# def test_partial_update_item_type(client):
#     updated_item_type = {"name": "Super coole nieuwe naam voor de test item_type"}
#     response = client.patch(
#         "/item_types/" + str(test_item_type["id"]),
#         json=updated_item_type,
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json()["name"] == updated_item_type["name"]
#     response_get_item_type = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert response_get_item_type.status_code == 200
#     assert response_get_item_type.json()["name"] == updated_item_type["name"]


# def test_delete_item_type_no_api_key(client):
#     response = client.delete("/item_types/" + str(test_item_type["id"]))
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200


# def test_archive_item_type_invalid_api_key(client):
#     response = client.delete(
#         "/item_types/" + str(test_item_type["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/item_types/" + str(test_item_type["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["is_archived"] == False


# def test_archive_item_type_invalid_id(client):
#     response = client.delete("/item_types/invalidId", headers=test_headers)
#     assert response.status_code == 422


# def test_archive_item_type_not_found(client):
#     response = client.delete(
#         "/item_types/" + str(non_existent_id), headers=test_headers
#     )
#     assert response.status_code == 404


def test_archive_item_type(client):
    response = client.delete(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert response.status_code == 200
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_archive_item_type_already_archived(client):
    response = client.delete(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert response.status_code == 400
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_no_api_key(client):
    response = client.patch("/item_types/" + str(test_item_type["id"]) + "/unarchive")
    assert response.status_code == 403
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_invalid_api_key(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive",
        headers=invalid_headers,
    )
    assert response.status_code == 403
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_invalid_id(client):
    response = client.patch("/item_types/invalidId/unarchive", headers=test_headers)
    assert response.status_code == 422


def test_unarchive_item_type_not_found(client):
    response = client.patch(
        "/item_types/" + str(non_existent_id) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_item_type(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 200
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == False


def test_unarchive_item_type_already_unarchived(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 400
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == False


def test_archive_item_type_invalid_id(client):
    response = client.delete("/item_types/invalidId", headers=test_headers)
    assert response.status_code == 422


def test_archive_item_type_not_found(client):
    response = client.delete(
        "/item_types/" + str(non_existent_id), headers=test_headers
    )
    assert response.status_code == 404


def test_archive_item_type(client):
    response = client.delete(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert response.status_code == 200
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_archive_item_type_already_archived(client):
    response = client.delete(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert response.status_code == 400
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_no_api_key(client):
    response = client.patch("/item_types/" + str(test_item_type["id"]) + "/unarchive")
    assert response.status_code == 403
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_invalid_api_key(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive",
        headers=invalid_headers,
    )
    assert response.status_code == 403
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == True


def test_unarchive_item_type_invalid_id(client):
    response = client.patch("/item_types/invalidId/unarchive", headers=test_headers)
    assert response.status_code == 422


def test_unarchive_item_type_not_found(client):
    response = client.patch(
        "/item_types/" + str(non_existent_id) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_item_type(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 200
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == False


def test_unarchive_item_type_already_unarchived(client):
    response = client.patch(
        "/item_types/" + str(test_item_type["id"]) + "/unarchive", headers=test_headers
    )
    assert response.status_code == 400
    responseGet = client.get(
        "/item_types/" + str(test_item_type["id"]), headers=test_headers
    )
    assert responseGet.status_code == 200
    assert responseGet.json()["is_archived"] == False
