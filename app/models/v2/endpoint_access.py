from models.v2.base import Base

class EndpointAccess(Base):
    class Config:
        table_name = "endpoint_access"

    endpoint: str
    full: bool
    get: bool | None = None
    post: bool | None = None
    put: bool | None = None
    delete: bool | None = None