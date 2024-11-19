# import pytest
# import httpx
# from tests.integration.test_globals import *

# test_transfer = {
#     "id": 99999999999999999,
#     "reference": "TR00001",
#     "transfer_from": None,
#     "transfer_to": 9229,
#     "transfer_status": "Completed",
#     "created_at": "2000-03-11T13:11:14Z",
#     "updated_at": "2000-03-12T16:11:14Z",
#     "items": [{"item_id": "P007435", "amount": 23}],
# }


# @pytest.fixture
# def client():
#     with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
#         yield client


# def test_get_all_transfers(client):
#     response = client.get("/transfers/", headers=test_headers)
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# def test_get_all_transfers_no_api_key(client):
#     response = client.get("/transfers/")
#     assert response.status_code == 403


# def test_get_all_transfers_invalid_api_key(client):
#     response = client.get("/transfers/", headers=invalid_headers)
#     assert response.status_code == 403


# def test_add_transfer(client):
#     response = client.post("/transfers/", json=test_transfer, headers=test_headers)
#     assert response.status_code == 201 or response.status_code == 200
#     assert response.json()["id"] == test_transfer["id"]


# def test_add_transfer_no_api_key(client):
#     response = client.post("/transfers/", json=test_transfer)
#     assert response.status_code == 403


# def test_add_transfer_invalid_api_key(client):
#     response = client.post("/transfers/", json=test_transfer, headers=invalid_headers)
#     assert response.status_code == 403


# def test_add_existing_transfer(client):
#     response = client.post("/transfers/", json=test_transfer, headers=test_headers)
#     assert response.status_code == 409


# def test_get_transfer_by_id(client):
#     response = client.get(
#         "/transfers/" + str(test_transfer["id"]), headers=test_headers
#     )
#     assert response.status_code == 200
#     response_json = response.json()
#     assert response_json is not None
#     assert isinstance(response_json, dict)


# def test_get_transfer_by_non_existent_id(client):
#     response = client.get("/transfers/" + str(non_existent_id), headers=test_headers)
#     assert response.status_code == 404
#     response_json = response.json()
#     assert response_json is not None
#     assert response_json["detail"] == "Transfer not found"


# def test_get_transfer_by_invalid_id(client):
#     response = client.get("/transfers/invalid_id", headers=test_headers)
#     assert response.status_code == 422


# def test_get_transfer_no_api_key(client):
#     response = client.get("/transfers/" + str(test_transfer["id"]))
#     assert response.status_code == 403


# def test_get_transfer_invalid_api_key(client):
#     response = client.get(
#         "/transfers/" + str(test_transfer["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_get_transfer_items(client):
#     response = client.get(
#         f"/transfers/{str(test_transfer['id'])}/items", headers=test_headers
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# def test_get_transfer_items_no_api_key(client):
#     response = client.get(f"/transfers/{str(test_transfer['id'])}/items")
#     assert response.status_code == 403


# def test_get_transfer_items_invalid_api_key(client):
#     response = client.get(
#         f"/transfers/{str(test_transfer['id'])}/items", headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_update_transfer(client):
#     updated_item_group = test_transfer.copy()
#     updated_item_group["reference"] = "TR00002"
#     response = client.put(
#         "/transfers/" + str(test_transfer["id"]),
#         json=updated_item_group,
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json()["id"] == test_transfer["id"]
#     assert response.json()["reference"] == "TR00002"


# def test_update_transfer_no_api_key(client):
#     updated_item_group = test_transfer.copy()
#     updated_item_group["reference"] = "TR00002"
#     response = client.put(
#         "/transfers/" + str(test_transfer["id"]), json=updated_item_group
#     )
#     assert response.status_code == 403


# def test_update_transfer_invalid_api_key(client):
#     updated_item_group = test_transfer.copy()
#     updated_item_group["reference"] = "TR00002"
#     response = client.put(
#         "/transfers/" + str(test_transfer["id"]),
#         json=updated_item_group,
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403


# def test_update_non_existent_transfer(client):
#     updated_item_group = test_transfer.copy()
#     updated_item_group["reference"] = "TR00002"
#     response = client.put(
#         "/transfers/" + str(non_existent_id),
#         json=updated_item_group,
#         headers=test_headers,
#     )
#     assert response.status_code == 404
#     response_json = response.json()
#     assert response_json is not None
#     assert response_json["detail"] == "Transfer not found"


# def test_update_invalid_transfer_id(client):
#     updated_item_group = test_transfer.copy()
#     updated_item_group["reference"] = "TR00002"
#     response = client.put(
#         "/transfers/invalid_id", json=updated_item_group, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_partial_update_transfer(client):
#     response = client.patch(
#         "/transfers/" + str(test_transfer["id"]),
#         json={"reference": "TR00002"},
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json()["reference"] == "TR00002"


# def test_partial_update_transfer_no_api_key(client):
#     response = client.patch(
#         "/transfers/" + str(test_transfer["id"]), json={"reference": "TR00002"}
#     )
#     assert response.status_code == 403


# def test_partial_update_transfer_invalid_api_key(client):
#     response = client.patch(
#         "/transfers/" + str(test_transfer["id"]),
#         json={"reference": "TR00002"},
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403


# def test_partial_update_non_existent_transfer(client):
#     response = client.patch(
#         "/transfers/" + str(non_existent_id),
#         json={"reference": "TR00002"},
#         headers=test_headers,
#     )
#     assert response.status_code == 404
#     response_json = response.json()
#     assert response_json is not None
#     assert response_json["detail"] == "Transfer not found"


# def test_partial_update_invalid_transfer_id(client):
#     response = client.patch(
#         "/transfers/invalid_id", json={"reference": "TR00002"}, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_commit_transfer(client):
#     response = client.put(
#         "/transfers/" + str(test_transfer["id"]) + "/commit", headers=test_headers
#     )
#     assert response.status_code == 200


# def test_commit_transfer_no_api_key(client):
#     response = client.put("/transfers/" + str(test_transfer["id"]) + "/commit")
#     assert response.status_code == 403


# def test_commit_transfer_invalid_api_key(client):
#     response = client.put(
#         "/transfers/" + str(test_transfer["id"]) + "/commit", headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_commit_non_existent_transfer(client):
#     response = client.put(
#         "/transfers/" + str(non_existent_id) + "/commit", headers=test_headers
#     )
#     assert response.status_code == 404
#     response_json = response.json()
#     assert response_json is not None
#     assert response_json["detail"] == "Transfer not found"


# def test_commit_invalid_transfer_id(client):
#     response = client.put("/transfers/invalid_id/commit", headers=test_headers)
#     assert response.status_code == 422


# def test_delete_transfer(client):
#     response = client.delete(
#         "/transfers/" + str(test_transfer["id"]), headers=test_headers
#     )
#     assert response.status_code == 200


# def test_delete_transfer_no_api_key(client):
#     response = client.delete("/transfers/" + str(test_transfer["id"]))
#     assert response.status_code == 403


# def test_delete_transfer_invalid_api_key(client):
#     response = client.delete(
#         "/transfers/" + str(test_transfer["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_delete_non_existent_transfer(client):
#     response = client.delete("/transfers/" + str(non_existent_id), headers=test_headers)
#     assert response.status_code == 404
#     response_json = response.json()
#     assert response_json is not None
#     assert response_json["detail"] == "Transfer not found"


# def test_delete_invalid_transfer_id(client):
#     response = client.delete("/transfers/invalid_id", headers=test_headers)
#     assert response.status_code == 422
