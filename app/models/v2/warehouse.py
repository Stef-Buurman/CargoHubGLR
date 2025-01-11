from pydantic import BaseModel, EmailStr, root_validator
from models.v2.base import BaseWithArchived


class Contact(BaseModel):
    name: str
    phone: str
    email: EmailStr


class Warehouse(BaseWithArchived):
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

    @root_validator(pre=True)
    def transform_contact(cls, values):
        contact = values.get("contact")
        if contact:
            values["contact_name"] = contact.get("name")
            values["contact_phone"] = contact.get("phone")
            values["contact_email"] = contact.get("email")
        return values
