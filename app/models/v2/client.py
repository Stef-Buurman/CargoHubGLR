from models.v2.base import BaseWithArchived


class Client(BaseWithArchived):
    id: int | None = None
    name: str
    address: str
    city: str
    zip_code: str
    province: str | None = None
    country: str
    contact_name: str
    contact_phone: str
    contact_email: str
    created_at: str | None = None
    updated_at: str | None = None
