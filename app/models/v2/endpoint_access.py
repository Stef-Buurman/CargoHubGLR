from models.v2.base import Base

class EndpointAccessDetail(Base):
    full: bool
    get: bool | None = None
    post: bool | None = None
    put: bool | None = None
    delete: bool | None = None

class EndpointAccess(Base):
    class Config:
        table_name = "endpoint_access"

    warehouses: EndpointAccessDetail | None = None
    locations: EndpointAccessDetail | None = None
    transfers: EndpointAccessDetail | None = None
    items: EndpointAccessDetail | None = None
    item_lines: EndpointAccessDetail | None = None
    item_groups: EndpointAccessDetail | None = None
    item_types: EndpointAccessDetail | None = None
    suppliers: EndpointAccessDetail | None = None
    orders: EndpointAccessDetail | None = None
    clients: EndpointAccessDetail | None = None
    shipments: EndpointAccessDetail | None = None