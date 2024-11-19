from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

USERS = [
    {
        "api_key": "test_api_key",
        "app": "Integration_Tests",
        "endpoint_access": {"full": True},
    },
    {
        "api_key": "a1b2c3d4e5",
        "app": "CargoHUB Dashboard 1",
        "endpoint_access": {"full": True},
    },
    {
        "api_key": "f6g7h8i9j0",
        "app": "CargoHUB Dashboard 2",
        "endpoint_access": {
            "full": False,
            "warehouses": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "locations": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "transfers": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "items": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_lines": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_groups": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "item_types": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "suppliers": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "orders": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "clients": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
            "shipments": {
                "full": False,
                "get": True,
                "post": False,
                "put": False,
                "delete": False,
            },
        },
    },
]

_users = USERS


def init():
    global _users
    _users = USERS


def get_user(api_key):
    for x in _users:
        if x["api_key"] == api_key:
            return x
    return None


def has_access(user, path, method):
    access = user["endpoint_access"]
    if access["full"]:
        return True
    else:
        return access[path][method]


API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(request: Request, api_key_header: str = Security(api_key_header)):
    init()

    user = get_user(api_key_header)

    if user is None:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    segments = request.url.path.strip('/').split('/')
    third_item = segments[2] if len(segments) > 2 else None  
    if third_item == None:
        raise HTTPException(status_code=400)

    if has_access(user, third_item, request.method.lower()):
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="You don't have access to this operation"
        )
