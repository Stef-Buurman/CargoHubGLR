from typing import List
from .base import Base2
from .endpoint_access import EndpointAccess


class User(Base2):
    id: int | None = None
    api_key: str
    app: str
    full: bool
    endpoint_access: List[EndpointAccess]
