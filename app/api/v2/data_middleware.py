from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from services.v2 import data_provider_v2


class DataProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        data_provider_v2.fetch_background_tasks().add_task(data_provider_v2.init)

        response = await call_next(request)

        return response
