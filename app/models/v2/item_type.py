from models.v2.base import Base2


class ItemType(Base2):
    id: int | None = None
    name: str
    description: str
    created_at: str | None = None
    updated_at: str | None = None
