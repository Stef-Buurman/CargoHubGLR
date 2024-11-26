import os
import httpx

TEST_PORT = os.getenv("TEST_PORT", "8000")

MAIN_URL = f"http://localhost:{TEST_PORT}/api/v1"

MAIN_URL_V2 = f"http://localhost:{TEST_PORT}/api/v2"

non_existent_id = 999999999999999999

test_headers = {"Authorization": "test_api_key"}

invalid_headers = {"Authorization": "invalid_key"}

timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)
