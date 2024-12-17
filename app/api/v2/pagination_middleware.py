from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from services.v2.pagination_service import Pagination


class PaginationProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        page = int(request.query_params.get("page", 1))
        items_per_page = int(request.query_params.get("items_per_page", 50))
        request.state.pagination = Pagination(page=page, items_per_page=items_per_page)

        response = await call_next(request)
        return response
