import pytest
import httpx
from app.models.v2.endpoint_access import EndpointAccess
from app.models.v2.user import User
from test_globals import *

test_user: User = User(
    api_key="blablablablablab", app="Integration_Tests", full=True, endpoint_access=[]
)
test_user_2: User = User(
    api_key="blublublublublublub",
    app="CargoHUB Dashboard 1",
    full=False,
    endpoint_access=[
        EndpointAccess(
            endpoint="warehouses",
            full=False,
            get=True,
            post=False,
            put=False,
            delete=True,
        ),
        EndpointAccess(
            endpoint="locations",
            full=True,
            get=False,
            post=False,
            put=False,
            delete=False,
        ),
        EndpointAccess(
            endpoint="transfers",
            full=False,
            get=True,
            post=False,
            put=True,
            delete=False,
        ),
        EndpointAccess(
            endpoint="items", full=False, get=False, post=False, put=False, delete=False
        ),
        EndpointAccess(
            endpoint="item_lines", full=True, get=True, post=True, put=True, delete=True
        ),
        EndpointAccess(
            endpoint="item_groups",
            full=False,
            get=False,
            post=False,
            put=True,
            delete=True,
        ),
        EndpointAccess(
            endpoint="item_types",
            full=False,
            get=False,
            post=True,
            put=True,
            delete=False,
        ),
        EndpointAccess(
            endpoint="suppliers",
            full=False,
            get=False,
            post=True,
            put=False,
            delete=True,
        ),
        EndpointAccess(
            endpoint="orders", full=False, get=True, post=False, put=True, delete=False
        ),
        EndpointAccess(
            endpoint="clients", full=False, get=True, post=True, put=False, delete=False
        ),
        EndpointAccess(
            endpoint="shipments", full=False, get=True, post=True, put=True, delete=True
        ),
    ],
)


@pytest.fixture
def client():
    with httpx.Client(base_url=MAIN_URL_V2, timeout=timeout) as client:
        yield client


def test_get_all_users(client):
    response = client.get("/users", headers=test_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_all_users_no_api_key(client):
    response = client.get("/users")
    assert response.status_code == 403


def test_get_all_users_invalid_api_key(client):
    response = client.get("/users", headers=invalid_headers)
    assert response.status_code == 403


def test_add_user_no_api_key(client):
    response = client.post("/users", json=test_user.model_dump())
    assert response.status_code == 403


def test_add_user_invalid_api_key(client):
    response = client.post(
        "/users", json=test_user.model_dump(), headers=invalid_headers
    )
    assert response.status_code == 403


def test_add_user(client):
    response = client.post("/users", json=test_user.model_dump(), headers=test_headers)
    assert response.status_code == 201
    test_user.id = response.json()["id"]
    assert response.json()["api_key"] == test_user.api_key


def test_add_user_duplicate(client):
    response = client.post("/users", json=test_user.model_dump(), headers=test_headers)
    assert response.status_code == 400


def test_get_user(client):
    response = client.get(f"/users/{test_user.id}", headers=test_headers)
    assert response.status_code == 200
    assert response.json()["api_key"] == test_user.api_key


def test_get_user_no_api_key(client):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 403


def test_get_user_invalid_api_key(client):
    response = client.get(f"/users/{test_user.id}", headers=invalid_headers)
    assert response.status_code == 403


def test_get_user_not_found(client):
    response = client.get(f"/users/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_get_user_by_invalid_id(client):
    response = client.get(f"/users/invalid", headers=test_headers)
    assert response.status_code == 422


def test_update_user(client):
    new_user = test_user.model_copy()
    new_user.app = "Integration_Tests_Updated"
    response = client.put(
        f"/users/{test_user.id}", json=new_user.model_dump(), headers=test_headers
    )
    assert response.status_code == 200
    assert response.json()["app"] == new_user.app
    response_get = client.get(f"/users/{new_user.id}", headers=test_headers)
    assert response_get.json()["app"] == new_user.app


def test_update_user_no_api_key(client):
    new_user = test_user.model_copy()
    new_user.app = "Integration_Tests_Updated"
    response = client.put(f"/users/{test_user.id}", json=new_user.model_dump())
    assert response.status_code == 403


def test_update_user_invalid_api_key(client):
    new_user = test_user.model_copy()
    new_user.app = "Integration_Tests_Updated"
    response = client.put(
        f"/users/{test_user.id}", json=new_user.model_dump(), headers=invalid_headers
    )
    assert response.status_code == 403


def test_update_user_not_found(client):
    new_user = test_user.model_copy()
    new_user.app = "Integration_Tests_Updated"
    response = client.put(
        f"/users/{non_existent_id}", json=new_user.model_dump(), headers=test_headers
    )
    assert response.status_code == 404


def test_update_user_by_invalid_id(client):
    new_user = test_user.model_copy()
    new_user.app = "Integration_Tests_Updated"
    response = client.put(
        f"/users/invalid", json=new_user.model_dump(), headers=test_headers
    )
    assert response.status_code == 422


def test_archive_user_no_api_key(client):
    response = client.delete(f"/users/{test_user.id}")
    assert response.status_code == 403


def test_archive_user_invalid_api_key(client):
    response = client.delete(f"/users/{test_user.id}", headers=invalid_headers)
    assert response.status_code == 403


def test_archive_user_not_found(client):
    response = client.delete(f"/users/{non_existent_id}", headers=test_headers)
    assert response.status_code == 404


def test_archive_user_invalid_id(client):
    response = client.delete(f"/users/invalid", headers=test_headers)
    assert response.status_code == 422


def test_archive_user(client):
    response = client.delete(f"/users/{test_user.id}", headers=test_headers)
    assert response.status_code == 200
    assert response.json()["is_archived"] is True
    response_get = client.get(f"/users/{test_user.id}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["is_archived"] is True


def test_already_archive_user(client):
    response = client.delete(f"/users/{test_user.id}", headers=test_headers)
    assert response.status_code == 400


def test_update_user_archived(client):
    response = client.put(
        f"/users/{test_user.id}", json=test_user.model_dump(), headers=test_headers
    )
    assert response.status_code == 400


def test_partial_update_user_archived(client):
    response = client.patch(
        f"/users/{test_user.id}", json=test_user.model_dump(), headers=test_headers
    )
    assert response.status_code == 400


def test_unarchive_user(client):
    response = client.patch(
        f"/users/{test_user.id}/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 200
    assert response.json()["is_archived"] is False
    response_get = client.get(f"/users/{test_user.id}", headers=test_headers)
    assert response_get.status_code == 200
    assert response_get.json()["is_archived"] is False


def test_already_unarchive_user(client):
    response = client.patch(f"/users/{test_user.id}/unarchive", headers=test_headers)
    assert response.status_code == 400


def test_unarchive_user_no_api_key(client):
    response = client.patch(f"/users/{test_user.id}/unarchive", json={})
    assert response.status_code == 403


def test_unarchive_user_invalid_api_key(client):
    response = client.patch(
        f"/users/{test_user.id}/unarchive", json={}, headers=invalid_headers
    )
    assert response.status_code == 403


def test_unarchive_user_not_found(client):
    response = client.patch(
        f"/users/{non_existent_id}/unarchive", json={}, headers=test_headers
    )
    assert response.status_code == 404


def test_unarchive_user_invalid_id(client):
    response = client.patch(f"/users/invalid/unarchive", headers=test_headers)
    assert response.status_code == 422
