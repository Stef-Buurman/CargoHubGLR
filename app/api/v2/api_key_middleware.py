from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from services.v2 import auth_provider_v2
from utils.globals import open_url_points


class ApiKeyProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in open_url_points:
            return await call_next(request)

        api_key = request.headers.get("Authorization")

        if not api_key:
            return JSONResponse(
                status_code=403, content={"detail": "No API Key provided"}
            )

        try:
            auth_provider_v2.get_api_key(request, api_key)
        except HTTPException as http_exc:
            return JSONResponse(
                status_code=http_exc.status_code, content={"detail": http_exc.detail}
            )
        except Exception as error:
            return JSONResponse(
                status_code=500, content={"detail": "Internal Server Error"}
            )

        response = await call_next(request)
        return response
