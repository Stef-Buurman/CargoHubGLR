# import pytest
# import httpx
# from tests.integration.test_globals import *

# test_location = {
#     "id": 999999999999999999999999999999999,
#     "warehouse_id": 9,
#     "code": "K.14.0",
#     "name": "Row: K, Rack: 14, Shelf: 0",
#     "created_at": "1988-05-28 04:55:53",
#     "updated_at": "1988-05-28 04:55:53",
# }


# @pytest.fixture
# def client():
#     with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
#         yield client


# def test_get_all_locations(client):
#     response = client.get("/locations/", headers=test_headers)
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# def test_get_all_locations_no_api_key(client):
#     response = client.get("/locations/")
#     assert response.status_code == 403


# def test_get_all_locations_invalid_api_key(client):
#     response = client.get("/locations/", headers=invalid_headers)
#     assert response.status_code == 403


# def test_add_location_no_api_key(client):
#     response = client.post("/locations/", json=test_location)
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 404


# def test_add_location_invalid_api_key(client):
#     response = client.post("/locations/", json=test_location, headers=invalid_headers)
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 404


# def test_add_location(client):
#     response = client.post("/locations/", json=test_location, headers=test_headers)
#     assert response.status_code == 201 or response.status_code == 200
#     assert response.json()["id"] == test_location["id"]


# def test_add_existing_location(client):
#     response = client.post("/locations/", json=test_location, headers=test_headers)
#     assert response.status_code == 409


# def test_get_location_by_id(client):
#     response = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert response.status_code == 200
#     assert response.json() is not None
#     assert isinstance(response.json(), dict)
#     assert response.json()["id"] == test_location["id"]


# def test_get_location_no_api_key(client):
#     response = client.get("/locations/" + str(test_location["id"]))
#     assert response.status_code == 403


# def test_get_location_invalid_api_key(client):
#     response = client.get(
#         "/locations/" + str(test_location["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403


# def test_get_non_existing_location_id(client):
#     response = client.get("/locations/" + str(non_existent_id), headers=test_headers)
#     assert response.status_code == 404


# def test_get_location_by_invalid_id(client):
#     response = client.get("/locations/asdabsdasdhasj", headers=test_headers)
#     assert response.status_code == 422


# def test_update_location_no_api_key(client):
#     response = client.put("/locations/" + str(test_location["id"]), json=test_location)
#     assert response.status_code == 403


# def test_update_location_invalid_api_key(client):
#     response = client.put(
#         "/locations/" + str(test_location["id"]),
#         json=test_location,
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403


# def test_update_non_existent_location(client):
#     response = client.put(
#         "/locations/" + str(non_existent_id), json=test_location, headers=test_headers
#     )
#     assert response.status_code == 404


# def test_update_invalid_location_id(client):
#     response = client.put(
#         "/locations/invalid_id", json=test_location, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_update_location(client):
#     test_location_copy = test_location.copy()
#     test_location_copy["name"] = "Row: kip, Rack: 1290, Shelf: 3467"
#     response = client.put(
#         "/locations/" + str(test_location_copy["id"]),
#         json=test_location_copy,
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json() is not None
#     assert isinstance(response.json(), dict)
#     responseGet = client.get(
#         "/locations/" + str(test_location_copy["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["name"] == test_location_copy["name"]


# def test_partial_update_location_no_api_key(client):
#     response = client.patch(
#         "/locations/" + str(test_location["id"]), json=test_location
#     )
#     assert response.status_code == 403


# def test_partial_update_location_invalid_api_key(client):
#     response = client.patch(
#         "/locations/" + str(test_location["id"]),
#         json=test_location,
#         headers=invalid_headers,
#     )
#     assert response.status_code == 403


# def test_partial_update_non_existent_location(client):
#     response = client.patch(
#         "/locations/" + str(non_existent_id), json=test_location, headers=test_headers
#     )
#     assert response.status_code == 404


# def test_partial_update_invalid_location_id(client):
#     response = client.patch(
#         "/locations/invalid_id", json=test_location, headers=test_headers
#     )
#     assert response.status_code == 422


# def test_partial_update_location(client):
#     new_name = "Row: kip, Rack: 1290, Shelf: 3467"
#     response = client.patch(
#         "/locations/" + str(test_location["id"]),
#         json={"name": new_name},
#         headers=test_headers,
#     )
#     assert response.status_code == 200
#     assert response.json() is not None
#     assert isinstance(response.json(), dict)
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200
#     assert responseGet.json()["name"] == new_name


# def test_delete_location_no_api_key(client):
#     response = client.delete("/locations/" + str(test_location["id"]))
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200


# def test_delete_location_invalid_api_key(client):
#     response = client.delete(
#         "/locations/" + str(test_location["id"]), headers=invalid_headers
#     )
#     assert response.status_code == 403
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 200


# def test_delete_non_existent_location(client):
#     response = client.delete("/locations/" + str(non_existent_id), headers=test_headers)
#     assert response.status_code == 404


# def test_delete_invalid_location_id(client):
#     response = client.delete("/locations/invalid_id", headers=test_headers)
#     assert response.status_code == 422


# def test_delete_location(client):
#     response = client.delete(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert response.status_code == 200
#     responseGet = client.get(
#         "/locations/" + str(test_location["id"]), headers=test_headers
#     )
#     assert responseGet.status_code == 404
