from models.v2.base import Base
from .endpoint_access import EndpointAccess

class User(Base):
    id: int | None = None
    api_key: str
    app: str
    full: bool
    endpoint_access: EndpointAccess | None = None