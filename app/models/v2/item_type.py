from pydantic import BaseModel


class ItemType(BaseModel):
    id: int | None = None
    name: str
    description: str
    created_at: str | None = None
    updated_at: str | None = None
