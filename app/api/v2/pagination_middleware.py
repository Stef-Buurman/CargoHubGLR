from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.v2.pagination_service import Pagination


class PaginationProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            return JSONResponse(
                status_code=422, content={"detail": "Invalid page number"}
            )

        try:
            items_per_page = int(request.query_params.get("items_per_page", 50))
        except ValueError:
            return JSONResponse(
                status_code=422, content={"detail": "Invalid items_per_page number"}
            )
        request.state.pagination = Pagination(page=page, items_per_page=items_per_page)

        response = await call_next(request)
        return response
