from pydantic import EmailStr
from models.v2.base import Base


class Contact(Base):
    name: str
    phone: str
    email: EmailStr


class Warehouse(Base):
    id: int | None = None
    code: str
    name: str
    address: str
    zip: str
    city: str
    province: str
    country: str
    contact: Contact
    created_at: str | None = None
    updated_at: str | None = None


class WarehouseDB(Base):
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
