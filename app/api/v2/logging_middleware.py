import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from services.v1 import data_provider
from services.v2 import data_provider_v2


info_logger = logging.getLogger("infoLogger")
info_logger.setLevel(logging.INFO)
info_logger.propagate = False


info_file_handler = logging.FileHandler("application.log")
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
info_logger.addHandler(info_file_handler)


info_stream_handler = logging.StreamHandler()
info_stream_handler.setLevel(logging.INFO)
info_stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
info_logger.addHandler(info_stream_handler)


error_logger = logging.getLogger("errorLogger")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False


error_file_handler = logging.FileHandler("error.log")
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
error_logger.addHandler(error_file_handler)


error_stream_handler = logging.StreamHandler()
error_stream_handler.setLevel(logging.ERROR)
error_stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
error_logger.addHandler(error_stream_handler)


async def get_previous_data(request: Request):
    path_parts = request.url.path.split("/")

    if len(path_parts) > 2:
        # version = path_parts[2] if len(path_parts) > 2 else None
        resource_type = path_parts[3] if len(path_parts) > 3 else None
        id = path_parts[4] if len(path_parts) > 4 else None

        if resource_type == "users" and id:
            return await data_provider_v2.fetch_user_pool().get_user_by_id(id)
        elif resource_type == "orders" and id:
            return data_provider_v2.fetch_order_pool().get_order(id)
        elif resource_type == "shipments" and id:
            return await data_provider_v2.fetch_shipment_pool().get_shipment(id)

    return {}


class LoggingProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        info_logger.info(f"Request: {request.method} {request.url.path}")

        try:

            request_body = await request.body()
            if request_body:
                body = json.loads(request_body)
                if isinstance(body, dict):
                    info_logger.info(f"SourceId: {body.get('source_id')}")
                else:
                    info_logger.warning("Request body is not a dictionary")
                # info_logger.info(f"Request Body: {body}")
        except json.JSONDecodeError:
            info_logger.warning("Failed to parse request body as JSON")

        try:
            if request.method == "POST":
                info_logger.info("Previous Data: None")
            elif request.method in ["PUT", "DELETE"]:
                try:
                    previous_data = await get_previous_data(request)
                    info_logger.info(
                        f"Previous Data: {json.dumps(previous_data, default=lambda o: o.__dict__)}"
                    )
                except Exception as e:
                    error_logger.error(
                        f"Error occurred while fetching previous data: {e}",
                        exc_info=True,
                    )
            elif request.method == "PATCH":
                try:
                    path_parts = request.url.path.split("/")
                    request_body = await request.json()
                    previous_data = await get_previous_data(request)

                    if len(path_parts) > 5 and path_parts[5] == "unarchive":
                        filtered_previous_data = {
                            "is_archived": getattr(previous_data, "is_archived", None)
                        }
                    else:
                        filtered_previous_data = {
                            k: getattr(previous_data, k, None)
                            for k in request_body.keys()
                        }
                    info_logger.info(
                        f"Previous Data: {json.dumps(filtered_previous_data, default=lambda o: o.__dict__)}"
                    )
                except Exception as e:
                    error_logger.error(
                        f"Error occurred while fetching previous data: {e}",
                        exc_info=True,
                    )

            response = await call_next(request)

            if request.method in ["POST", "PUT", "DELETE"]:
                response_body = b"".join(
                    [section async for section in response.body_iterator]
                )

                async def new_body_iterator():
                    yield response_body

                response.body_iterator = new_body_iterator()
                info_logger.info(f"New Data: {response_body.decode('utf-8')}")
                info_logger.info(f"Response: {response.status_code}")
            elif request.method == "PATCH":
                response_body = b"".join(
                    [section async for section in response.body_iterator]
                )

                async def new_body_iterator():
                    yield response_body

                response.body_iterator = new_body_iterator()
                updated_fields = json.loads(response_body.decode("utf-8"))
                request_body = await request.json()
                path_parts = request.url.path.split("/")

                if len(path_parts) > 5 and path_parts[5] == "unarchive":
                    filtered_updated_fields = {
                        "is_archived": updated_fields.get("is_archived", None)
                    }
                else:
                    filtered_updated_fields = {
                        k: updated_fields.get(k) for k in request_body.keys()
                    }
                info_logger.info(f"New Data: {json.dumps(filtered_updated_fields)}")
                info_logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:

            error_logger.error(
                f"Error occurred while processing the request: {e}", exc_info=True
            )
            raise e
