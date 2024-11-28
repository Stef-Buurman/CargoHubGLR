import pytest
import httpx
from tests.integration.test_globals import *

test_item_line = {
    "id": 999,
    "name": "Test Item Line",
    "description": "",
    "created_at": "2022-08-18 07:05:25",
    "updated_at": "2023-05-15 15:44:28",
}

test_item_1 = {
    "code": "fake1",
    "description": "fake1",
    "short_description": "fake1",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 999,
    "item_group": 12,
    "item_type": 12,
    "unit_purchase_quantity": 47,
    "unit_order_quantity": 13,
    "pack_order_quantity": 11,
    "supplier_id": 55,
    "supplier_code": "SUP9999",
    "supplier_part_number": "E-86805-uTM",
}

test_item_2 = {
    "code": "fake2",
    "description": "fake2",
    "short_description": "fake2",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 999,
    "item_group": 12,
    "item_type": 12,
    "unit_purchase_quantity": 47,
    "unit_order_quantity": 13,
    "pack_order_quantity": 11,
    "supplier_id": 55,
    "supplier_code": "SUP9999",
    "supplier_part_number": "E-86806-uTM",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_item_lines(client):
    response = client.get("/item_lines/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_item_lines_no_api_key(client):
    response = client.get("/item_lines/")
    assert response.status_code == 403


def test_get_all_item_lines_invalid_api_key(client):
    response = client.get("/item_lines/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_item_line_no_api_key(client):
    response = client.post("/item_lines/", json=test_item_line)
    assert response.status_code == 403
    responseGet = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_item_line_invalid_api_key(client):
    response = client.post("/item_lines/", json=test_item_line, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_item_line(client):
    response = client.post("/item_lines/", json=test_item_line, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_item_line["id"] = response.json()["id"]
    assert response.json()["id"] == test_item_line["id"]


# def test_add_existing_item_line(client):
#     response = client.post("/item_lines/", json=test_item_line, headers=test_headers)
#     assert response.status_code == 409


def test_get_item_line_by_id(client):
    response = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_item_line["id"]


def test_get_item_line_by_invalid_id(client):
    response = client.get("/item_lines/asdabsdasdhasj", headers=test_headers)
    assert response.status_code == 422


def test_get_item_line_non_existent_id(client):
    response = client.get("/item_lines/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_item_line_no_api_key(client):
    response = client.get("/item_lines/" + str(test_item_line["id"]))
    assert response.status_code == 403


def test_get_item_line_invalid_api_key(client):
    response = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


# def test_get_item_line_items_no_items(client):
#     response = client.get(f'/item_lines/{str(test_item_line["id"])}/items', headers=test_headers)
#     assert response.status_code == 204


def test_get_item_line_items_no_api_key(client):
    response = client.get(f'/item_lines/{str(test_item_line["id"])}/items')
    assert response.status_code == 403


def test_get_item_line_items_invalid_api_key(client):
    response = client.get(
        f'/item_lines/{str(test_item_line["id"])}/items', headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_item_line_items_invalid_id(client):
    response = client.get("/item_lines/invalid_id/items", headers=test_headers)
    assert response.status_code == 422


def test_get_items_for_item_line_not_found(client):
    response = client.get(
        "/item_lines/" + str(non_existent_id) + "/items", headers=test_headers
    )
    assert response.status_code == 404


def test_get_item_line_items(client):
    test_item_1["item_line"] = test_item_line["id"]
    response_post_fake_item_1 = client.post(
        "/items/", json=test_item_1, headers=test_headers
    )
    test_item_2["item_line"] = test_item_line["id"]
    response_post_fake_item_2 = client.post(
        "/items/", json=test_item_2, headers=test_headers
    )
    assert (
        response_post_fake_item_1.status_code == 201
        or response_post_fake_item_1.status_code == 200
    )
    assert (
        response_post_fake_item_2.status_code == 201
        or response_post_fake_item_2.status_code == 200
    )

    response = client.get(
        f"/item_lines/{test_item_line['id']}/items", headers=test_headers
    )
    response_items = response.json()["data"]
    assert response.status_code == 200
    assert len(response_items) == 2
    assert response_items[0]["code"] == response_post_fake_item_1.json()["code"]
    assert response_items[1]["code"] == response_post_fake_item_2.json()["code"]

    for item in response_items:
        assert item["item_line"] == test_item_line["id"]

    response_delete_item_1 = client.delete(
        "/items/" + response_post_fake_item_1.json()["uid"], headers=test_headers
    )
    assert response_delete_item_1.status_code == 200
    response_delete_item_2 = client.delete(
        "/items/" + response_post_fake_item_2.json()["uid"], headers=test_headers
    )
    assert response_delete_item_2.status_code == 200


def test_update_item_line_no_api_key(client):
    updated_item_line = test_item_line.copy()
    updated_item_line["description"] = "updated item line"
    response = client.put(
        "/item_lines/" + str(updated_item_line["id"]), json=updated_item_line
    )
    assert response.status_code == 403
    response_get_item_line = client.get(
        "/item_lines/" + str(updated_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200
    assert response_get_item_line.json()["description"] == test_item_line["description"]


def test_update_item_line_invalid_api_key(client):
    updated_item_line = test_item_line.copy()
    updated_item_line["description"] = "updated item line"
    response = client.put(
        "/item_lines/" + str(updated_item_line["id"]),
        json=updated_item_line,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_item_line = client.get(
        "/item_lines/" + str(updated_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200
    assert response_get_item_line.json()["description"] == test_item_line["description"]


def test_update_item_line_invalid_id(client):
    updated_item_line = test_item_line.copy()
    updated_item_line["description"] = "updated item line"
    response = client.put(
        "/item_lines/invalid_id", json=updated_item_line, headers=test_headers
    )
    assert response.status_code == 422


def test_update_item_line_non_existent_id(client):
    updated_item_line = test_item_line.copy()
    updated_item_line["description"] = "updated item line"
    response = client.put(
        "/item_lines/" + str(non_existent_id),
        json=updated_item_line,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_update_item_line(client):
    updated_item_line = test_item_line.copy()
    updated_item_line["description"] = "updated item line"
    response = client.put(
        "/item_lines/" + str(updated_item_line["id"]),
        json=updated_item_line,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_item_line = client.get(
        "/item_lines/" + str(updated_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200
    assert (
        response_get_item_line.json()["description"] == updated_item_line["description"]
    )


def test_partial_update_item_line_no_api_key(client):
    updated_item_line = {"description": "updated item line"}
    response = client.patch(
        "/item_lines/" + str(test_item_line["id"]), json=updated_item_line
    )
    assert response.status_code == 403


def test_partial_update_item_line_invalid_api_key(client):
    updated_item_line = {"description": "updated item line"}
    response = client.patch(
        "/item_lines/" + str(test_item_line["id"]),
        json=updated_item_line,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_item_line_invalid_id(client):
    updated_item_line = {"description": "updated item line"}
    response = client.patch(
        "/item_lines/invalid_id", json=updated_item_line, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_item_line_non_existent_id(client):
    updated_item_line = {"description": "updated item line"}
    response = client.patch(
        "/item_lines/" + str(non_existent_id),
        json=updated_item_line,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_partial_update_item_line(client):
    updated_item_line = {"description": "updated item line"}
    response = client.patch(
        "/item_lines/" + str(test_item_line["id"]),
        json=updated_item_line,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_item_line = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200
    assert (
        response_get_item_line.json()["description"] == updated_item_line["description"]
    )


def test_delete_item_line_no_api_key(client):
    response = client.delete("/item_lines/" + str(test_item_line["id"]))
    assert response.status_code == 403
    response_get_item_line = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200


def test_delete_item_line_invalid_api_key(client):
    response = client.delete(
        "/item_lines/" + str(test_item_line["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_item_line = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200


def test_delete_item_line_invalid_id(client):
    response = client.delete("/item_lines/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_delete_item_line_non_existent_id(client):
    response = client.delete(
        "/item_lines/" + str(non_existent_id), headers=test_headers
    )
    assert response.status_code == 404
    response_get_item_line = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 200


def test_delete_item_line(client):
    response = client.delete(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_item_line = client.get(
        "/item_lines/" + str(test_item_line["id"]), headers=test_headers
    )
    assert response_get_item_line.status_code == 404
