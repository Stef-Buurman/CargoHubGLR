from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from services.v2 import data_provider_v2
from models.v2.user import User

user_router_v2 = APIRouter(tags=["v2.Users"], prefix="/users")


@user_router_v2.get("/{user_id}")
def read_user(user_id: int):
    user = data_provider_v2.fetch_user_pool().get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router_v2.get("")
def read_users(request: Request):
    users = data_provider_v2.fetch_user_pool().get_users()
    if users is None:
        raise HTTPException(status_code=404, detail="No users found")
    return request.state.pagination.apply(users)


@user_router_v2.post("")
def create_user(user: User):
    created_user = data_provider_v2.fetch_user_pool().add_new_user(user)
    if created_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_user.model_dump()
    )


@user_router_v2.put("/{user_id}")
def update_user(user_id: int, user: User):
    existing_user = data_provider_v2.fetch_user_pool().is_user_archived(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif existing_user:
        raise HTTPException(status_code=400, detail="User is archived")
    updated_user = data_provider_v2.fetch_user_pool().update_user(user_id, user)
    return updated_user


@user_router_v2.patch("/{user_id}")
def partial_update_user(user_id: int, user: dict):
    existing_user = data_provider_v2.fetch_user_pool().is_user_archived(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif existing_user:
        raise HTTPException(status_code=400, detail="User is archived")

    existing_user = data_provider_v2.fetch_user_pool().is_user_archived(user_id)

    valid_keys = User.model_fields.keys()
    update_data = {key: value for key, value in user.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_user, key, value)
    updated_user = data_provider_v2.fetch_user_pool().update_user(
        user_id, existing_user
    )
    return updated_user


@user_router_v2.delete("/{user_id}")
def delete_user(user_id: int):
    existing_user = data_provider_v2.fetch_user_pool().is_user_archived(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif existing_user:
        raise HTTPException(status_code=400, detail="User is archived")
    updated_user = data_provider_v2.fetch_user_pool().archive_user(user_id)
    return updated_user


@user_router_v2.patch("/{user_id}/unarchive")
def unarchive_user(user_id: int):
    existing_user = data_provider_v2.fetch_user_pool().is_user_archived(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif not existing_user:
        raise HTTPException(status_code=400, detail="User is not archived")
    updated_user = data_provider_v2.fetch_user_pool().unarchive_user(user_id)
    return updated_user
