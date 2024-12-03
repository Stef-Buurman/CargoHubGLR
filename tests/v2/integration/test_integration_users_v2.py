import pytest
from app.models.v2.endpoint_access import EndpointAccess
from app.models.v2.user import User
from app.services.v2.model_services.user_service import UserService
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
def user_service():
    user_service = UserService()
    yield user_service


def test_get_all_users(user_service):
    users = user_service.get_users()
    assert isinstance(users, list)


def test_add_user(user_service):
    user_service.add_user(
        test_user.api_key, test_user.app, test_user.full, test_user.endpoint_access
    )
    users = user_service.get_users()
    for user in users:
        if user.api_key == test_user.api_key:
            assert user.app == test_user.app
            assert user.full == test_user.full
            assert user.endpoint_access == test_user.endpoint_access


def test_get_user_by_api_key(user_service):
    user = user_service.get_user(test_user.api_key)
    assert user.api_key == test_user.api_key


def test_has_access_warehouses(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "warehouses", "get") == True
    assert user_service.has_access(user.api_key, "warehouses", "delete") == True
    assert user_service.has_access(user.api_key, "warehouses", "post") == False
    assert user_service.has_access(user.api_key, "warehouses", "put") == False
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_locations(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "locations", "get") == True
    assert user_service.has_access(user.api_key, "locations", "delete") == True
    assert user_service.has_access(user.api_key, "locations", "post") == True
    assert user_service.has_access(user.api_key, "locations", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_transfers(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "transfers", "get") == True
    assert user_service.has_access(user.api_key, "transfers", "delete") == False
    assert user_service.has_access(user.api_key, "transfers", "post") == False
    assert user_service.has_access(user.api_key, "transfers", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_items(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "items", "get") == False
    assert user_service.has_access(user.api_key, "items", "delete") == False
    assert user_service.has_access(user.api_key, "items", "post") == False
    assert user_service.has_access(user.api_key, "items", "put") == False
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_item_lines(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "item_lines", "get") == True
    assert user_service.has_access(user.api_key, "item_lines", "delete") == True
    assert user_service.has_access(user.api_key, "item_lines", "post") == True
    assert user_service.has_access(user.api_key, "item_lines", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_item_groups(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "item_groups", "get") == False
    assert user_service.has_access(user.api_key, "item_groups", "delete") == True
    assert user_service.has_access(user.api_key, "item_groups", "post") == False
    assert user_service.has_access(user.api_key, "item_groups", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_item_types(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "item_types", "get") == False
    assert user_service.has_access(user.api_key, "item_types", "delete") == False
    assert user_service.has_access(user.api_key, "item_types", "post") == True
    assert user_service.has_access(user.api_key, "item_types", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_suppliers(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "suppliers", "get") == False
    assert user_service.has_access(user.api_key, "suppliers", "delete") == True
    assert user_service.has_access(user.api_key, "suppliers", "post") == True
    assert user_service.has_access(user.api_key, "suppliers", "put") == False
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_orders(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "orders", "get") == True
    assert user_service.has_access(user.api_key, "orders", "delete") == False
    assert user_service.has_access(user.api_key, "orders", "post") == False
    assert user_service.has_access(user.api_key, "orders", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_clients(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "clients", "get") == True
    assert user_service.has_access(user.api_key, "clients", "delete") == False
    assert user_service.has_access(user.api_key, "clients", "post") == True
    assert user_service.has_access(user.api_key, "clients", "put") == False
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_has_access_shipments(user_service):
    user = user_service.add_user(
        test_user_2.api_key,
        test_user_2.app,
        test_user_2.full,
        test_user_2.endpoint_access,
    )
    assert user is not None
    assert user_service.has_access(user.api_key, "shipments", "get") == True
    assert user_service.has_access(user.api_key, "shipments", "delete") == True
    assert user_service.has_access(user.api_key, "shipments", "post") == True
    assert user_service.has_access(user.api_key, "shipments", "put") == True
    user_service.delete_user(test_user_2.api_key)
    assert user_service.get_user(test_user_2.api_key) == None
    assert user_service.get_user(test_user_2.api_key, True) == None


def test_delete_user(user_service):
    user_service.delete_user(test_user.api_key)
    users = user_service.get_users(True)
    for user in users:
        assert user.api_key != test_user.api_key
