from pydantic import BaseModel


class ItemLine(BaseModel):
    id: int | None = None
    name: str
    description: str
    created_at: str | None = None
    updated_at: str | None = None