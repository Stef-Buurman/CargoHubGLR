from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from services.v2 import auth_provider_v2


class ApiKeyProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("Authorization")

        if not api_key:
            raise HTTPException(status_code=403, detail="No API Key provided")

        try:
            auth_provider_v2.get_api_key(request, api_key)
        except Exception as error:
            raise HTTPException(status_code=403, detail=str(error))

        response = await call_next(request)
        return response
