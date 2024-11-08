import httpx


MAIN_URL = "http://localhost:8000/api/v1"

MAIN_URL_V2 = "http://localhost:8000/api/v2"

non_existent_id = 99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999

test_headers = {"Authorization": "test_api_key"}

invalid_headers = {"Authorization": "invalid_key"}

timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)
