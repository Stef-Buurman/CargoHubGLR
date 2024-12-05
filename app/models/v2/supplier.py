from models.v2.base import Base2


class Supplier(Base2):
    id: int | None = None
    code: str
    name: str
    address: str
    address_extra: str
    city: str
    zip_code: str
    province: str
    country: str
    contact_name: str
    phonenumber: str
    reference: str
    created_at: str | None = None
    updated_at: str | None = None
