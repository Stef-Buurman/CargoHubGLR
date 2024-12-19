import os
import httpx

TEST_PORT = os.getenv("TEST_PORT", "8000")

MAIN_URL = f"http://localhost:{TEST_PORT}/api/v1"

MAIN_URL_V2 = f"http://localhost:{TEST_PORT}/api/v2"

non_existent_id = 999999999999999999

test_headers = {"Authorization": "test_api_key"}

invalid_headers = {"Authorization": "invalid_key"}

timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)

pagination_url_base = "?page="
pagination_url_negative = "?page=-1"
pagination_url_0 = "?page=0"
pagination_url_1 = "?page=1"
pagination_url_2 = "?page=2"

wrong_page_1 = "?page=1.5"
wrong_page_2 = "?page=-1.5"
wrong_page_3 = "?page=page"
wrong_page_4 = "?page=%^%^%^%^%^"
