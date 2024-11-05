from pydantic import BaseModel, EmailStr


class Contact(BaseModel):
    name: str
    phone: str
    email: EmailStr


class Warehouse(BaseModel):
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
