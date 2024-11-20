from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from services import data_provider_v2

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(request: Request, api_key_header: str = Security(api_key_header)) -> str:
    user = data_provider_v2.fetch_user_pool().get_user(api_key_header)

    if user is None:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    segments = request.url.path.strip("/").split("/")
    third_item = segments[2] if len(segments) > 2 else None
    if third_item == None:
        raise HTTPException(status_code=400)

    if data_provider_v2.fetch_user_pool().has_access(
        user.api_key, third_item, request.method.lower()
    ):
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="You don't have access to this operation"
        )
