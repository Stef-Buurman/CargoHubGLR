from pydantic import BaseModel


class ItemInObject(BaseModel):
    item_id: str
    amount: int
