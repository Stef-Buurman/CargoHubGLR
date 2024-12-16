from pydantic import BaseModel
from models.v2.base import Base


class ItemInObject(Base):
    item_id: str
    amount: int
