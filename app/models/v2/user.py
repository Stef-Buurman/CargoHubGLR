from typing import List
from .base import BaseWithArchived
from .endpoint_access import EndpointAccess




class User(BaseWithArchived):
    id: int | None = None
    api_key: str
    app: str
    full: bool
    endpoint_access: List[EndpointAccess]
