import logging
import json
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from services.v2 import data_provider_v2

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

logs_path = os.path.join(PROJECT_PATH, "logs")
if not os.path.exists(logs_path):
    os.makedirs(logs_path)

info_logger = logging.getLogger("infoLogger")
info_logger.setLevel(logging.INFO)
info_logger.propagate = False

info_file_handler = logging.FileHandler(PROJECT_PATH + "/logs/application.log")
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
info_logger.addHandler(info_file_handler)

error_logger = logging.getLogger("errorLogger")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False

error_file_handler = logging.FileHandler(PROJECT_PATH + "/logs/error.log")
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
error_logger.addHandler(error_file_handler)


async def get_previous_data(request: Request):
    path_parts = request.url.path.split("/")

    if len(path_parts) > 2:
        resource_type = path_parts[3] if len(path_parts) > 3 else None
        id = path_parts[4] if len(path_parts) > 4 else None

        if resource_type == "users" and id:
            return data_provider_v2.fetch_user_pool().get_user_by_id(id, True)
        elif resource_type == "orders" and id:
            data = data_provider_v2.fetch_order_pool().get_order(id)

            if data and data.items:
                data.items = [
                    {"item_id": item.item_id, "amount": item.amount}
                    for item in data.items
                ]

            return data
        elif resource_type == "shipments" and id:
            data = data_provider_v2.fetch_shipment_pool().get_shipment(id)

            if data and data.items:
                data.items = [
                    {"item_id": item.item_id, "amount": item.amount}
                    for item in data.items
                ]

            return data

    return {}


class LoggingProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"] and any(
            resource in request.url.path
            for resource in ["users", "orders", "shipments"]
        ):

            info_logger.info(f"Request: {request.method} {request.url.path}")

            try:
                request_body = await request.body()
                if request_body:
                    body = json.loads(request_body)
                    if isinstance(body, dict):
                        info_logger.info(f"Source_id: {body.get('source_id')}")
                    else:
                        info_logger.warning("Request body is not a dictionary")
            except json.JSONDecodeError:
                info_logger.warning("Failed to parse request body as JSON")

            try:
                previous_data = await get_previous_data(request)
                response = await call_next(request)
                response_body = b"".join(
                    [section async for section in response.body_iterator]
                )
                path_parts = request.url.path.split("/")

                async def new_body_iterator():
                    yield response_body

                response.body_iterator = new_body_iterator()

                if request.method == "POST":
                    info_logger.info("Previous Data: None")
                    info_logger.info(f"New Data: {response_body.decode('utf-8')}")
                elif request.method in ["PUT", "PATCH"] and len(path_parts) <= 5:
                    request_body = await request.json()
                    updated_fields = json.loads(response_body.decode("utf-8"))
                    if isinstance(request_body, dict):
                        filtered_previous_data = {
                            k: getattr(previous_data, k, None)
                            for k in request_body.keys()
                            if k not in ["source_id", "id"]
                            and getattr(previous_data, k, None) != request_body[k]
                        }
                        filtered_updated_fields = {
                            k: updated_fields.get(k)
                            for k in request_body.keys()
                            if k not in ["source_id", "id"]
                            and getattr(previous_data, k, None) != updated_fields.get(k)
                        }
                    else:
                        filtered_previous_data = {}
                        filtered_updated_fields = {}

                    info_logger.info(
                        f"Previous Data: {json.dumps(filtered_previous_data, default=lambda o: o.__dict__)}"
                    )
                    info_logger.info(f"New Data: {json.dumps(filtered_updated_fields)}")
                elif request.method == "DELETE" or (
                    request.method == "PATCH"
                    and len(path_parts) >= 6
                    and path_parts[5] == "unarchive"
                ):
                    deleted_data = json.loads(response_body.decode("utf-8"))
                    is_archived_value = {
                        "is_archived": deleted_data.get("is_archived", None)
                    }
                    info_logger.info(
                        f"Previous Data: {json.dumps({'is_archived': getattr(previous_data, 'is_archived', None)})}"
                    )
                    info_logger.info(f"New Data: {json.dumps(is_archived_value)}")

                info_logger.info(f"Response: {response.status_code}")
                return response
            except Exception as e:
                error_logger.error(
                    f"Error occurred while processing the request: {e}", exc_info=True
                )
                raise e
        else:
            response = await call_next(request)
            return response
