from .base import Base1


class EndpointAccess(Base1):
    class Config:
        table_name = "endpoint_access"

    endpoint: str
    full: bool
    get: bool | None = None
    post: bool | None = None
    put: bool | None = None
    delete: bool | None = None
