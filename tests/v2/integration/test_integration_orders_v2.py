import pytest
import httpx
from test_globals import *

test_order = {
    "id": 99999999999999999,
    "source_id": 52,
    "order_date": "1983-09-26T19:06:08Z",
    "request_date": "1983-09-30T19:06:08Z",
    "reference": "ORD00003",
    "reference_extra": "Vergeven kamer goed enkele wiel tussen.",
    "order_status": "Delivered",
    "notes": "Zeil hoeveel onze map sex ding.",
    "shipping_notes": "Ontvangen schoon voorzichtig instrument ster vijver kunnen raam.",
    "picking_notes": "Grof geven politie suiker bodem zuid.",
    "warehouse_id": 11,
    "ship_to": None,
    "bill_to": None,
    "shipment_id": 3,
    "total_amount": 1156.14,
    "total_discount": 420.45,
    "total_tax": 677.42,
    "total_surcharge": 86.03,
    "created_at": "1983-09-26T19:06:08Z",
    "updated_at": "1983-09-28T15:06:08Z",
    "items": [
        {"item_id": "P010669", "amount": 16},
        {"item_id": "P010670", "amount": 17},
        {"item_id": "P010671", "amount": 18},
    ],
}


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_orders(client):
    response = client.get("/orders", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_orders_no_api_key(client):
    response = client.get("/orders")
    assert response.status_code == 403


def test_get_all_orders_invalid_api_key(client):
    response = client.get("/orders", headers=invalid_headers)
    assert response.status_code == 403


def test_add_order_no_api_key(client):
    response = client.post("/orders", json=test_order)
    assert response.status_code == 403
    responseGet = client.get("/orders/" + str(test_order["id"]), headers=test_headers)
    assert responseGet.status_code == 404


def test_add_order_invalid_api_key(client):
    response = client.post("/orders", json=test_order, headers=invalid_headers)
    assert response.status_code == 403
    responseGet = client.get("/orders/" + str(test_order["id"]), headers=test_headers)
    assert responseGet.status_code == 404


def test_add_order(client):
    response = client.post("/orders", json=test_order, headers=test_headers)
    assert response.status_code == 201 or response.status_code == 200
    test_order["id"] = response.json()["id"]


def test_get_order_by_id(client):
    response = client.get("/orders/" + str(test_order["id"]), headers=test_headers)
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_order["id"]


def test_get_order_by_invalid_id(client):
    response = client.get("/orders/asdabsdasdhasj", headers=test_headers)
    assert response.status_code == 422


def test_get_order_non_existent_id(client):
    response = client.get("/orders/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404


def test_get_order_no_api_key(client):
    response = client.get("/orders/" + str(test_order["id"]))
    assert response.status_code == 403


def test_get_order_invalid_api_key(client):
    response = client.get("/orders/" + str(test_order["id"]), headers=invalid_headers)
    assert response.status_code == 403


def test_get_order_items(client):
    response = client.get(
        f'/orders/{str(test_order["id"])}/items', headers=test_headers
    )
    response_items = response.json()["data"]
    assert response.status_code == 200
    assert isinstance(response_items, list)
    assert len(response_items) == len(test_order["items"])
    for i, item in enumerate(response_items):
        assert item["item_id"] == test_order["items"][i]["item_id"]
        assert item["amount"] == test_order["items"][i]["amount"]


def test_get_order_items_no_api_key(client):
    response = client.get(f'/orders/{str(test_order["id"])}/items')
    assert response.status_code == 403


def test_get_order_items_invalid_api_key(client):
    response = client.get(
        f'/orders/{str(test_order["id"])}/items', headers=invalid_headers
    )
    assert response.status_code == 403


def test_get_order_items_invalid_id(client):
    response = client.get("/orders/invalid_id/items", headers=test_headers)
    assert response.status_code == 422


def test_update_order_no_api_key(client):
    updated_order = test_order.copy()
    updated_order["total_amount"] = test_order["total_amount"] + 100
    response = client.put("/orders/" + str(updated_order["id"]), json=updated_order)
    assert response.status_code == 403
    response_get_order = client.get(
        "/orders/" + str(updated_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["total_amount"] == test_order["total_amount"]


def test_update_order_invalid_api_key(client):
    updated_order = test_order.copy()
    updated_order["total_amount"] = test_order["total_amount"] + 100
    response = client.put(
        "/orders/" + str(updated_order["id"]),
        json=updated_order,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_order = client.get(
        "/orders/" + str(updated_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["total_amount"] == test_order["total_amount"]


def test_update_order_invalid_id(client):
    updated_order = test_order.copy()
    updated_order["total_amount"] = test_order["total_amount"] + 100
    response = client.put(
        "/orders/invalid_id", json=updated_order, headers=test_headers
    )
    assert response.status_code == 422


def test_update_order_non_existent_id(client):
    updated_order = test_order.copy()
    updated_order["total_amount"] = test_order["total_amount"] + 100
    response = client.put(
        "/orders/" + str(non_existent_id), json=updated_order, headers=test_headers
    )
    assert response.status_code == 404


def test_update_order(client):
    updated_order = test_order.copy()
    updated_order["total_amount"] = test_order["total_amount"] + 100
    response = client.put(
        "/orders/" + str(updated_order["id"]), json=updated_order, headers=test_headers
    )
    assert response.status_code == 200
    response_get_order = client.get(
        "/orders/" + str(updated_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["total_amount"] == test_order["total_amount"] + 100


def test_update_order_items_no_api_key(client):
    test_order_items = test_order["items"].copy()
    test_order_items.append({"item_id": "P010672", "amount": 19})
    response = client.put(
        f'/orders/{str(test_order["id"])}/items', json=test_order_items
    )
    assert response.status_code == 403
    response_get_order = client.get(
        f'/orders/{str(test_order["id"])}/items', headers=test_headers
    )
    response_data = response_get_order.json()["data"]
    assert response_get_order.status_code == 200
    assert len(response_data) == len(test_order["items"])
    for i in range(len(response_data)):
        assert response_data[i - 1]["item_id"] == test_order["items"][i - 1]["item_id"]
        assert response_data[i - 1]["amount"] == test_order["items"][i - 1]["amount"]


def test_update_order_items_invalid_api_key(client):
    test_order_items = test_order["items"].copy()
    test_order_items.append({"item_id": "P010672", "amount": 19})
    response = client.put(
        f'/orders/{str(test_order["id"])}/items',
        json=test_order_items,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get_order = client.get(
        f'/orders/{str(test_order["id"])}/items', headers=test_headers
    )
    response_data = response_get_order.json()["data"]
    assert response_get_order.status_code == 200
    assert len(response_data) == len(test_order["items"])
    for i in range(len(response_data)):
        assert response_data[i - 1]["item_id"] == test_order["items"][i - 1]["item_id"]
        assert response_data[i - 1]["amount"] == test_order["items"][i - 1]["amount"]


def test_update_order_items_invalid_id(client):
    test_order_items = test_order["items"].copy()
    test_order_items.append({"item_id": "P010672", "amount": 19})
    response = client.put(
        "/orders/invalid_id/items", json=test_order_items, headers=test_headers
    )
    assert response.status_code == 422


def test_update_order_items_non_existent_id(client):
    test_order_items = test_order["items"].copy()
    test_order_items.append({"item_id": "P010672", "amount": 19})
    response = client.put(
        f"/orders/{str(non_existent_id)}/items",
        json=test_order_items,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_update_order_items(client):
    test_order_items = test_order["items"].copy()
    test_order_items.append({"item_id": "P010672", "amount": 19})
    response = client.put(
        f'/orders/{str(test_order["id"])}/items',
        json=test_order_items,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_order = client.get(
        f'/orders/{str(test_order["id"])}/items', headers=test_headers
    )
    response_data = response_get_order.json()["data"]
    assert response_get_order.status_code == 200
    assert len(response_data) == len(test_order_items)
    for i in range(len(response_data)):
        assert response_data[i - 1]["item_id"] == test_order_items[i - 1]["item_id"]
        assert response_data[i - 1]["amount"] == test_order_items[i - 1]["amount"]


def test_partial_update_order_no_api_key(client):
    updated_order = {"notes": "This order has been patched."}
    response = client.patch("/orders/" + str(test_order["id"]), json=updated_order)
    assert response.status_code == 403


def test_partial_update_order_invalid_api_key(client):
    updated_order = {"notes": "This order has been patched."}
    response = client.patch(
        "/orders/" + str(test_order["id"]),
        json=updated_order,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_order_invalid_id(client):
    updated_order = {"notes": "This order has been patched."}
    response = client.patch(
        "/orders/invalid_id", json=updated_order, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_order_non_existent_id(client):
    updated_order = {"notes": "This order has been patched."}
    response = client.patch(
        "/orders/" + str(non_existent_id),
        json=updated_order,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_partial_update_order(client):
    updated_order = {"notes": "This order has been patched."}
    response = client.patch(
        "/orders/" + str(test_order["id"]),
        json=updated_order,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["notes"] == updated_order["notes"]


def test_archive_order_no_api_key(client):
    response = client.delete("/orders/" + str(test_order["id"]))
    assert response.status_code == 403

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200


def test_archive_order_invalid_api_key(client):
    response = client.delete(
        "/orders/" + str(test_order["id"]), headers=invalid_headers
    )
    assert response.status_code == 403

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200


def test_archive_order_invalid_id(client):
    response = client.delete("/orders/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_archive_order_non_existent_id(client):
    response = client.delete("/orders/" + str(non_existent_id), headers=test_headers)
    assert response.status_code == 404

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200


def test_archive_order(client):
    response = client.delete("/orders/" + str(test_order["id"]), headers=test_headers)
    assert response.status_code == 200

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is True


def test_archive_already_archived_order(client):
    response = client.delete("/orders/" + str(test_order["id"]), headers=test_headers)
    assert response.status_code == 400
    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is True


def test_unarchive_order(client):
    response = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 200
    response_get_order = client.get(
        f"/orders/{str(test_order['id'])}", headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is False


def test_unarchive_order_no_api_key(client):
    response = client.patch(f"/orders/{str(test_order['id'])}/unarchive", json={})
    assert response.status_code == 403


def test_unarchive_order_invalid_api_key(client):
    response = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=invalid_headers
    )
    assert response.status_code == 403


def test_unarchive_order_invalid_id(client):
    response = client.patch(
        "/orders/invalid_id/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 422


def test_unarchive_order_non_existent_id(client):
    response = client.patch(
        f"/orders/{str(non_existent_id)}/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_already_unarchived_order(client):
    response = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 400
    response_get_order = client.get(
        f"/orders/{str(test_order['id'])}", headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is False


def test_update_archived_order(client):
    response_delete = client.delete(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_delete.status_code == 200

    response = client.put(
        "/orders/" + str(test_order["id"]), json=test_order, headers=test_headers
    )
    assert response.status_code == 400

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is True

    response_unarchive = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=test_headers
    )
    assert response_unarchive.status_code == 200


def test_partial_update_archived_order(client):
    response_delete = client.delete(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_delete.status_code == 200

    response = client.patch(
        "/orders/" + str(test_order["id"]),
        json={"notes": "This order has been patched."},
        headers=test_headers,
    )
    assert response.status_code == 400

    response_get_order = client.get(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is True
    response_unarchive = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=test_headers
    )
    assert response_unarchive.status_code == 200


def test_update_order_items_archived_order(client):
    response_delete = client.delete(
        "/orders/" + str(test_order["id"]), headers=test_headers
    )
    assert response_delete.status_code == 200

    response = client.put(
        f'/orders/{str(test_order["id"])}/items',
        json=test_order["items"],
        headers=test_headers,
    )
    assert response.status_code == 400

    response_get_order = client.get(
        f'/orders/{str(test_order["id"])}', headers=test_headers
    )
    assert response_get_order.status_code == 200
    assert response_get_order.json()["is_archived"] is True

    response_unarchive = client.patch(
        f"/orders/{str(test_order['id'])}/unarchive", json={}, headers=test_headers
    )
    assert response_unarchive.status_code == 200
