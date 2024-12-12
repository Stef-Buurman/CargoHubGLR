import httpx
import pytest
from test_globals import *

test_shipment = {
    "id": 999999999,
    "order_id": 900,
    "source_id": 900,
    "order_date": "1973-01-28",
    "request_date": "1973-01-30",
    "shipment_date": "1973-02-01",
    "shipment_type": "I",
    "shipment_status": "Pending",
    "notes": "Hoog genot springen afspraak mond bus.",
    "carrier_code": "DHL",
    "carrier_description": "DHL Express",
    "service_code": "NextDay",
    "payment_type": "Automatic",
    "transfer_mode": "Ground",
    "total_package_count": 29,
    "total_package_weight": 463.0,
    "created_at": "1973-01-28T20:09:11Z",
    "updated_at": "1973-01-29T22:09:11Z",
    "items": [
        {"item_id": "P010669", "amount": 16},
        {"item_id": "P020333", "amount": 5},
        {"item_id": "P045782", "amount": 8},
    ],
}

test_order_1 = {
    "id": 1,
    "source_id": 33,
    "order_date": "2019-04-03T11:33:15Z",
    "request_date": "2019-04-07T11:33:15Z",
    "reference": "ORD00001",
    "reference_extra": "Bedreven arm straffen bureau.",
    "order_status": "Delivered",
    "notes": "Voedsel vijf vork heel.",
    "shipping_notes": "Buurman betalen plaats bewolkt.",
    "picking_notes": "Ademen fijn volgorde scherp aardappel op leren.",
    "warehouse_id": 18,
    "ship_to": 4562,
    "bill_to": 7863,
    "shipment_id": 1,
    "total_amount": 9905.13,
    "total_discount": 150.77,
    "total_tax": 372.72,
    "total_surcharge": 77.6,
    "created_at": "2019-04-03T11:33:15Z",
    "updated_at": "2019-04-05T07:33:15Z",
    "items": [
        {"item_id": "P019969", "amount": 16},
        {"item_id": "P020333", "amount": 5},
        {"item_id": "P045782", "amount": 8},
    ]
}

test_order_2 = {
    "id": 1,
    "source_id": 33,
    "order_date": "2019-04-03T11:33:15Z",
    "request_date": "2019-04-07T11:33:15Z",
    "reference": "ORD00001",
    "reference_extra": "Bedreven arm straffen bureau.",
    "order_status": "Delivered",
    "notes": "Voedsel vijf vork heel.",
    "shipping_notes": "Buurman betalen plaats bewolkt.",
    "picking_notes": "Ademen fijn volgorde scherp aardappel op leren.",
    "warehouse_id": 18,
    "ship_to": 4562,
    "bill_to": 7863,
    "shipment_id": 1,
    "total_amount": 9905.13,
    "total_discount": 150.77,
    "total_tax": 372.72,
    "total_surcharge": 77.6,
    "created_at": "2019-04-03T11:33:15Z",
    "updated_at": "2019-04-05T07:33:15Z",
    "items": [
        {"item_id": "P019969", "amount": 16},
        {"item_id": "P020333", "amount": 5},
        {"item_id": "P045782", "amount": 8},
    ]
}

item_to_add= {"item_id": "P019969", "amount": 16}

@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_shipments(client):
    response = client.get("/shipments/", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_shipments_no_api_key(client):
    response = client.get("/shipments/")
    assert response.status_code == 403


def test_get_all_shipments_invalid_api_key(client):
    response = client.get("/shipments/", headers=invalid_headers)
    assert response.status_code == 403


def test_add_shipment_no_api_key(client):
    response = client.post("/shipments/", json=test_shipment)
    assert response.status_code == 403
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 404


def test_add_shipment_invalid_api_key(client):
    response = client.post("/shipments/", json=test_shipment, headers=invalid_headers)
    assert response.status_code == 403
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 404


def test_add_shipment(client):
    response = client.post("/shipments/", json=test_shipment, headers=test_headers)
    assert response.status_code in [200, 201]
    test_shipment["id"] = response.json()["id"]
    assert response.json()["id"] == test_shipment["id"]


def test_get_shipment_by_id(client):
    response = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response.status_code == 200
    assert response.json() is not None
    assert isinstance(response.json(), dict)
    assert response.json()["id"] == test_shipment["id"]


def test_get_shipment_no_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}")
    assert response.status_code == 403


def test_get_shipment_invalid_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}", headers=invalid_headers)
    assert response.status_code == 403


def test_get_invalid_shipment_id(client):
    response = client.get("/shipments/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_get_nonexistent_shipment(client):
    response = client.get(f"/shipments/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_update_shipment_no_api_key(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["shipment_status"] = "Shipped"
    response = client.put(f"/shipments/{test_shipment['id']}", json=updated_shipment)
    assert response.status_code == 403
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["shipment_status"] == test_shipment["shipment_status"]


def test_update_shipment_invalid_api_key(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["shipment_status"] = "Shipped"
    response = client.put(
        f"/shipments/{test_shipment['id']}",
        json=updated_shipment,
        headers=invalid_headers,
    )
    assert response.status_code == 403
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["shipment_status"] == test_shipment["shipment_status"]


def test_update_invalid_shipment_id(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["shipment_status"] = "Shipped"
    response = client.put(
        "/shipments/invalid_id", json=updated_shipment, headers=test_headers
    )
    assert response.status_code == 422


def test_update_nonexistent_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["shipment_status"] = "Shipped"
    response = client.put(
        f"/shipments/{non_existent_id}", json=updated_shipment, headers=test_headers
    )
    assert response.status_code == 404


def test_update_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["shipment_status"] = "Shipped"
    response = client.put(
        f"/shipments/{test_shipment['id']}", json=updated_shipment, headers=test_headers
    )
    assert response.status_code == 200
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["shipment_status"] == updated_shipment["shipment_status"]


def test_partial_update_shipment_no_api_key(client):
    updated_shipment = {"notes": "Super coole nieuwe note voor de test shipment"}
    response = client.patch(
        "/shipments/" + str(test_shipment["id"]), json=updated_shipment
    )
    assert response.status_code == 403


def test_partial_update_shipment_invalid_api_key(client):
    updated_shipment = {"notes": "Super coole nieuwe note voor de test shipment"}
    response = client.patch(
        "/shipments/" + str(test_shipment["id"]),
        json=updated_shipment,
        headers=invalid_headers,
    )
    assert response.status_code == 403


def test_partial_update_shipment_invalid_id(client):
    updated_shipment = {"notes": "Super coole nieuwe note voor de test shipment"}
    response = client.patch(
        "/shipments/invalid_id", json=updated_shipment, headers=test_headers
    )
    assert response.status_code == 422


def test_partial_update_shipment_non_existent_id(client):
    updated_shipment = {"notes": "Super coole nieuwe note voor de test shipment"}
    response = client.patch(
        "/shipments/" + str(non_existent_id),
        json=updated_shipment,
        headers=test_headers,
    )
    assert response.status_code == 404


def test_partial_update_shipment(client):
    updated_shipment = {"notes": "Super coole nieuwe note voor de test shipment"}
    response = client.patch(
        "/shipments/" + str(test_shipment["id"]),
        json=updated_shipment,
        headers=test_headers,
    )
    assert response.status_code == 200
    response_get_shipment = client.get(
        "/shipments/" + str(test_shipment["id"]), headers=test_headers
    )
    assert response_get_shipment.status_code == 200
    assert response_get_shipment.json()["notes"] == updated_shipment["notes"]


def test_add_items_to_shipment_no_api_key(client):
    items = test_shipment["items"]
    items.append(item_to_add)
    response = client.put(
        f"/shipments/{test_shipment['id']}/items", json=items
    )
    assert response.status_code == 403


def test_add_items_to_shipment_invalid_api_key(client):
    items = test_shipment["items"]
    items.append(item_to_add)
    response = client.put(
        f"/shipments/{test_shipment['id']}/items", json=items, headers=invalid_headers
    )
    assert response.status_code == 403


def test_add_items_to_shipment_invalid_shipment_id(client):
    items = test_shipment["items"]
    items.append(item_to_add)
    response = client.put(
        "/shipments/invalid_id/items", json=items, headers=test_headers
    )
    assert response.status_code == 422


def test_add_items_to_non_existent_shipment(client):
    items = test_shipment["items"]
    items.append(item_to_add)
    response = client.put(
        f"/shipments/{non_existent_id}/items", json=items, headers=test_headers
    )
    assert response.status_code == 404


def test_add_items_to_shipment(client):
    items = test_shipment["items"]
    items.append(item_to_add)
    removed_item = items.pop(0)
    response = client.put(
        f"/shipments/{test_shipment['id']}/items", json=items, headers=test_headers
    )
    assert response.status_code == 200
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert len(response_get.json()["items"]) == len(items)
    added_item = None
    removed_item_from_client = None
    test_shipment["items"] = response_get.json()["items"]
    print(test_shipment["items"])
    for item in response_get.json()["items"]:
        if item["item_id"] == item_to_add["item_id"]:
            added_item = item
        if item["item_id"] == removed_item["item_id"]:
            removed_item_from_client = item
    assert added_item is not None
    assert added_item["amount"] == item_to_add["amount"]
    assert removed_item_from_client is None


def test_get_items_for_shipment_no_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}/items")
    assert response.status_code == 403


def test_get_items_for_shipment_invalid_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}/items", headers=invalid_headers)
    assert response.status_code == 403


def test_get_items_for_shipment_invalid_shipment_id(client):
    response = client.get("/shipments/invalid_id/items", headers=test_headers)
    assert response.status_code == 422


def test_get_items_for_non_existent_shipment(client):
    response = client.get(f"/shipments/{non_existent_id}/items", headers=test_headers)
    assert response.status_code == 404


def test_get_items_for_shipment(client):
    response = client.get(f"/shipments/{test_shipment['id']}/items", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) == len(test_shipment["items"])
    for item in response.json()["data"]:
        assert item["item_id"] in [item["item_id"] for item in test_shipment["items"]]


def test_add_orders_to_shipment_no_api_key(client):
    response = client.put(
        f"/shipments/{test_shipment['id']}/orders", json=[test_order_1], headers=test_headers
    )
    assert response.status_code == 403


def test_add_orders_to_shipment_invalid_api_key(client):
    response = client.put(
        f"/shipments/{test_shipment['id']}/orders", json=[test_order_1], headers=invalid_headers
    )
    assert response.status_code == 403


def test_add_orders_to_shipment_invalid_shipment_id(client):
    response = client.put(
        "/shipments/invalid_id/orders", json=[test_order_1], headers=test_headers
    )
    assert response.status_code == 422


def test_add_orders_to_non_existent_shipment(client):
    response = client.put(
        f"/shipments/{non_existent_id}/orders", json=[test_order_1], headers=test_headers
    )
    assert response.status_code == 404


def test_add_orders_to_shipment(client):
    test_order_1["shipment_id"] = test_shipment["id"]
    test_order_2["shipment_id"] = test_shipment["id"]
    response_add_orders_1 = client.post(
        f"/orders/", json=test_order_1, headers=test_headers
    )
    assert response_add_orders_1.status_code is 201
    test_order_1["id"] = response_add_orders_1.json()["id"]
    response_add_orders_2 = client.post(
        f"/orders/", json=test_order_2, headers=test_headers
    )
    assert response_add_orders_2.status_code is 201
    test_order_2["id"] = response_add_orders_2.json()["id"]
    response = client.put(
        f"/shipments/{test_shipment['id']}/orders", json=[test_order_1], headers=test_headers
    )
    assert response.status_code == 200
    response_get_orders = client.get(
        f"/shipments/{test_shipment['id']}/orders", headers=test_headers
    )
    assert response_get_orders.status_code == 200
    assert len(response_get_orders.json()["data"]) == 1
    assert response_get_orders.json()["data"][0]["id"] == test_order_1["id"]
    response_get_single_order = client.get(
        f"/orders/{test_order_2['id']}", headers=test_headers
    )
    assert response_get_single_order.status_code == 200
    assert response_get_single_order.json()["shipment_id"] == -1
    assert response_get_single_order.json()["order_status"] == "Scheduled"
    


def test_get_orders_for_shipment_no_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}/orders")
    assert response.status_code == 403


def test_get_orders_for_shipment_invalid_api_key(client):
    response = client.get(f"/shipments/{test_shipment['id']}/orders", headers=invalid_headers)
    assert response.status_code == 403


def test_get_orders_for_shipment_invalid_shipment_id(client):
    response = client.get("/shipments/invalid_id/orders", headers=test_headers)
    assert response.status_code == 422


def test_get_orders_for_non_existent_shipment(client):
    response = client.get(f"/shipments/{non_existent_id}/orders", headers=test_headers)
    assert response.status_code == 404


def test_get_orders_for_shipment(client):
    response = client.get(f"/shipments/{test_shipment['id']}/orders", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["id"] == test_order_1["id"]


def test_commit_shipment_no_api_key(client):
    response = client.put(f"/shipments/{test_shipment['id']}/commit")
    assert response.status_code == 403


def test_commit_shipment_invalid_api_key(client):
    response = client.put(
        f"/shipments/{test_shipment['id']}/commit", headers=invalid_headers
    )
    assert response.status_code == 403


def test_commit_invalid_shipment_id(client):
    response = client.put("/shipments/invalid_id/commit", headers=test_headers)
    assert response.status_code == 422


def test_commit_non_existent_shipment(client):
    response = client.put(f"/shipments/{non_existent_id}/commit", headers=test_headers)
    assert response.status_code == 404


def test_commit_shipment_to_transit(client):
    response = client.put(f"/shipments/{test_shipment['id']}/commit", headers=test_headers)
    assert response.status_code == 200
    assert response.json()["shipment_status"] == "Transit"
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["shipment_status"] == "Transit"


def test_commit_shipment_to_delivered(client):
    response = client.put(f"/shipments/{test_shipment['id']}/commit", headers=test_headers)
    assert response.status_code == 200
    assert response.json()["shipment_status"] == "Delivered"
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["shipment_status"] == "Delivered"


def test_commit_shipment_already_delivered(client):
    response = client.put(f"/shipments/{test_shipment['id']}/commit", headers=test_headers)
    assert response.status_code == 400


def test_archive_shipment_no_api_key(client):
    response = client.delete(f"/shipments/{test_shipment['id']}")
    assert response.status_code == 403


def test_archive_shipment_invalid_api_key(client):
    response = client.delete(
        f"/shipments/{test_shipment['id']}", headers=invalid_headers
    )
    assert response.status_code == 403


def test_archive_invalid_shipment_id(client):
    response = client.delete("/shipments/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_archive_non_existent_shipment(client):
    response = client.delete(f"/shipments/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_archive_shipment(client):
    response = client.delete(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response.status_code == 200


def test_update_archived_shipment(client):
    updated_shipment = test_shipment.copy()
    updated_shipment["payment_type"] = "payment_type"
    response = client.put(
        f"/shipments/{test_shipment['id']}", json=updated_shipment, headers=test_headers
    )
    assert response.status_code == 400
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["payment_type"] == test_shipment["payment_type"]
    assert response_get.json()["is_archived"] is True


def test_commit_archived_shipment(client):
    response = client.put(f"/shipments/{test_shipment['id']}/commit", headers=test_headers)
    assert response.status_code == 400


def test_update_items_in_archived_shipment(client):
    updated_items = [
        {"item_id": "P019969", "amount": 16},
        {"item_id": "P020333", "amount": 5},
        {"item_id": "P045782", "amount": 8},
    ]
    response = client.put(
        f"/shipments/{test_shipment['id']}/items", json=updated_items, headers=test_headers
    )
    assert response.status_code == 400


def test_update_orders_in_archived_shipment(client):
    test_shipment_2 = test_shipment.copy()
    test_shipment_2["order_id"] = test_order_1["id"]
    response_add_orders = client.post(
        f"/orders/", json=test_order_1, headers=test_headers
    )
    assert response_add_orders.status_code is 201
    test_shipment["order_id"] = response_add_orders.json()["id"]
    test_order_1["id"] = response_add_orders.json()["id"]
    response_add = client.post(
        f"/shipments/", json=test_shipment_2, headers=test_headers
    )
    assert response_add.status_code is 201
    response_archive = client.delete(
        f"/shipments/{response_add.json()['id']}", headers=test_headers
    )
    assert response_archive.status_code == 200
    test_shipment_2["id"] = response_add.json()["id"]
    response = client.put(
        f"/shipments/{test_shipment_2['id']}/orders", json=[test_order_1], headers=test_headers
    )
    assert response.status_code == 400


def test_unarchive_shipment_no_api_key(client):
    response = client.patch(f"/shipments/{test_shipment['id']}/unarchive")
    assert response.status_code == 403


def test_unarchive_shipment_invalid_api_key(client):
    response = client.patch(
        f"/shipments/{test_shipment['id']}/unarchive", headers=invalid_headers
    )
    assert response.status_code == 403


def test_unarchive_invalid_shipment_id(client):
    response = client.patch("/shipments/invalid_id", headers=test_headers)
    assert response.status_code == 422


def test_unarchive_non_existent_shipment(client):
    response = client.patch(f"/shipments/{non_existent_id}/unarchive", headers=test_headers)
    assert response.status_code == 404


def test_unarchive_shipment(client):
    response = client.patch(
        f"/shipments/{test_shipment['id']}/unarchive", headers=test_headers
    )
    assert response.status_code == 200
    response_get = client.get(f"/shipments/{test_shipment['id']}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["is_archived"] is False
