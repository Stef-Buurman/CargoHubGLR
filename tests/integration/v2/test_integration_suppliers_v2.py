import pytest
import httpx
from tests.integration.test_globals import *

test_supplier = {
    "id": 9999,
    "code": "SUP9999",
    "name": "Super coole test supplier",
    "address": "6942 Yoe Bide N.",
    "address_extra": "Apt. 420",
    "city": "Port Sigmaburgh",
    "zip_code": "42069",
    "province": "Illinois",
    "country": "Czech Republic",
    "contact_name": "Joe Biden",
    "phonenumber": "363.541.7282x36825",
    "reference": "LPaJ-SUP9999",
}

test_item_1 = {
    "uid": "fake_item_1",
    "code": "fake1",
    "description": "fake1",
    "short_description": "fake1",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 12,
    "item_group": 12,
    "item_type": 12,
    "unit_purchase_quantity": 47,
    "unit_order_quantity": 13,
    "pack_order_quantity": 11,
    "supplier_id": 9999,
    "supplier_code": "SUP9999",
    "supplier_part_number": "E-86805-uTM",
}

test_item_2 = {
    "uid": "fake_item_2",
    "code": "fake2",
    "description": "fake2",
    "short_description": "fake2",
    "upc_code": "6523540947122",
    "model_number": "63-OFFTq0T",
    "commodity_code": "oTo304",
    "item_line": 12,
    "item_group": 12,
    "item_type": 12,
    "unit_purchase_quantity": 47,
    "unit_order_quantity": 13,
    "pack_order_quantity": 11,
    "supplier_id": 9999,
    "supplier_code": "SUP9999",
    "supplier_part_number": "E-86806-uTM",
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_suppliers(client):
    response = client.get("/suppliers/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_suppliers_no_api_key(client):
    response = client.get("/suppliers/")
    assert response.status_code == 403


def test_get_all_suppliers_invalid_api_key(client):
    response = client.get("/suppliers/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_supplier_no_api_key(client):
    response = client.post("/suppliers/", json=test_supplier)
    assert response.status_code == 403
    responseGet = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_supplier_invalid_api_key(client):
    response = client.post("/suppliers/", json=test_supplier, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert responseGet.status_code == 404


def test_add_supplier(client):
    response = client.post("/suppliers/", json=test_supplier, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    assert response.json()["id"] == test_supplier["id"]


def test_add_existing_supplier(client):
    response = client.post("/suppliers/", json=test_supplier, headers=test_headers)
    assert response.status_code == 409


def test_get_supplier_by_id(client):
    response = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_supplier["id"]


def test_get_supplier_by_invalid_id(client):
    response = client.get("/suppliers/an-invalid-id", headers=test_headers)
    assert response.status_code == 422


def test_get_supplier_non_existent_id(client):
    response = client.get("/suppliers/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_supplier_no_api_key(client):
    response = client.get("/suppliers/" + str(test_supplier["id"]))
    assert response.status_code == 403


def test_get_supplier_invalid_api_key(client):
    response = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=invalid_headers
    )
    assert response.status_code == 403


# def test_get_supplier_items_no_items(client):
#     response = client.get(f'/suppliers/{str(test_supplier["id"])}/items', headers=test_headers)
#     assert response.status_code == 204


def test_get_supplier_items_no_api_key(client):
    response = client.get(f'/suppliers/{str(test_supplier["id"])}/items')
    assert response.status_code == 403


def test_get_supplier_items_invalid_api_key(client):
    response = client.get(
        f'/suppliers/{str(test_supplier["id"])}/items', headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_supplier_items_invalid_id(client):
    response = client.get("/suppliers/invalid_id/items", headers=test_headers)
    assert response.status_code == 422


def test_get_supplier_items(client):
    response_post_fake_item_1 = client.post(
        "/items/", json=test_item_1, headers=test_headers
    )
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
        f"/suppliers/{test_supplier['id']}/items", headers=test_headers
    )

    assert response.status_code == 200

    response_items = response.json()
    assert len(response_items) == 2
    assert response_items[0]["code"] == test_item_1["code"]
    assert response_items[1]["code"] == test_item_2["code"]

    for item in response_items:
        assert item["supplier_id"] == test_supplier["id"]

    response_delete_item_1 = client.delete(
        "/items/" + test_item_1["uid"], headers=test_headers
    )
    assert response_delete_item_1.status_code == 200
    response_delete_item_2 = client.delete(
        "/items/" + test_item_2["uid"], headers=test_headers
    )
    assert response_delete_item_2.status_code == 200


def test_update_supplier_no_api_key(client):
    updated_supplier = test_supplier.copy()
    updated_supplier["name"] = "Super coole nieuwe naam voor de test supplier"
    response = client.put(
        "/suppliers/" + str(updated_supplier["id"]), json=updated_supplier
    )
    assert response.status_code == 403
    response_get_supplier = client.get(
        "/suppliers/" + str(updated_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200
    assert response_get_supplier.json()["name"] == test_supplier["name"]


def test_update_supplier_invalid_api_key(client):
    updated_supplier = test_supplier.copy()
    updated_supplier["name"] = "Super coole nieuwe naam voor de test supplier"
    response = client.put(
        "/suppliers/" + str(updated_supplier["id"]),
        json=updated_supplier,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_supplier = client.get(
        "/suppliers/" + str(updated_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200
    assert response_get_supplier.json()["name"] == test_supplier["name"]


def test_update_supplier_invalid_id(client):
    updated_supplier = test_supplier.copy()
    updated_supplier["name"] = "Super coole nieuwe naam voor de test supplier"
    response = client.put(
        "/suppliers/invalid_id", json=updated_supplier, headers=test_headers
    )
    assert response.status_code == 422


def test_update_supplier_non_existent_id(client):
    updated_supplier = test_supplier.copy()
    updated_supplier["name"] = "Super coole nieuwe naam voor de test supplier"
    response = client.put(
        "/suppliers/" + str(non_existent_id),
        json=updated_supplier,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_update_supplier(client):
    updated_supplier = test_supplier.copy()
    updated_supplier["name"] = "Super coole nieuwe naam voor de test supplier"
    response = client.put(
        "/suppliers/" + str(updated_supplier["id"]),
        json=updated_supplier,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_supplier = client.get(
        "/suppliers/" + str(updated_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200
    assert response_get_supplier.json()["name"] == updated_supplier["name"]


def test_delete_supplier_no_api_key(client):
    response = client.delete("/suppliers/" + str(test_supplier["id"]))
    assert response.status_code == 403
    response_get_supplier = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200


def test_delete_supplier_invalid_api_key(client):
    response = client.delete(
        "/suppliers/" + str(test_supplier["id"]), headers=invalid_headers
    )
    assert response.status_code == 403
    response_get_supplier = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200


def test_delete_supplier_invalid_id(client):
    response = client.delete("/suppliers/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_delete_supplier_non_existent_id(client):
    response = client.delete("/suppliers/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404
    response_get_supplier = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 200


def test_delete_supplier(client):
    response = client.delete(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response.status_code == 200
    response_get_supplier = client.get(
        "/suppliers/" + str(test_supplier["id"]), headers=test_headers
    )
    assert response_get_supplier.status_code == 404
