from typing import List
from models.v2.base import Base


class Inventory(Base):
    class Config:
        table_name = "inventories"

    id: int | None = None
    item_id: str
    description: str
    item_reference: str
    locations: List[int]
    total_on_hand: int
    total_expected: int
    total_ordered: int
    total_allocated: int
    total_available: int
    created_at: str | None = None
    updated_at: str | None = None
