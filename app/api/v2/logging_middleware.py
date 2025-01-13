import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


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


class LoggingProviderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        info_logger.info(f"Request: {request.method} {request.url.path}")

        try:

            request_body = await request.body()
            if request_body:
                body = json.loads(request_body)
                info_logger.info(f"SourceId: {body.get('source_id')}")
                # info_logger.info(f"Request Body: {body}")
        except json.JSONDecodeError:
            info_logger.warning("Failed to parse request body as JSON")

        try:
            response = await call_next(request)
            response_body = b"".join(
                [section async for section in response.body_iterator]
            )

            async def new_body_iterator():
                yield response_body

            response.body_iterator = new_body_iterator()
            info_logger.info(f"Response Body: {response_body.decode('utf-8')}")
            info_logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:

            error_logger.error(
                f"Error occurred while processing the request: {e}", exc_info=True
            )
            raise e
