from models.v2.base import BaseWithArchived


class Location(BaseWithArchived):
    id: int | None = None
    warehouse_id: int
    code: str
    name: str
    created_at: str | None = None
    updated_at: str | None = None
