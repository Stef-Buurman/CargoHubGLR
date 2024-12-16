from pydantic import EmailStr
from models.v2.base import Base2


class Warehouse(Base2):
    class Config:
        table_name = "warehouses"

    id: int | None = None
    code: str
    name: str
    address: str
    zip: str
    city: str
    province: str
    country: str
    contact_name: str
    contact_phone: str
    contact_email: EmailStr
    created_at: str | None = None
    updated_at: str | None = None
