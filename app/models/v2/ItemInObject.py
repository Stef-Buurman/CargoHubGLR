from pydantic import BaseModel
from models.v2.base import Base1


class ItemInObject(Base1):
    item_id: str
    amount: int
