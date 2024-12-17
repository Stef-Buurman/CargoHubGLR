import os
import uvicorn
from fastapi import FastAPI
from app.api.v2.api_key_middleware import ApiKeyProviderMiddleware
from app.api.v2.data_middleware import DataProviderMiddleware
from api.v1.routes import routers as v1_routers
from api.v2.routes import routers as v2_routers

app = FastAPI()

app.add_middleware(ApiKeyProviderMiddleware)
app.add_middleware(DataProviderMiddleware)

v1_url = "/api/v1"
v2_url = "/api/v2"

app.include_router(v1_routers, prefix=v1_url)
app.include_router(v2_routers, prefix=v2_url)


def main():
    app_port = int(os.getenv("TEST_PORT", 8000))
    uvicorn.run(app, port=app_port)


if __name__ == "__main__":
    main()
