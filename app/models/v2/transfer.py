from pydantic import BaseModel


class ItemInTransfer(BaseModel):
    item_id: str
    amount: int


class Transfer(BaseModel):
    id: int | None = None
    reference: str
    transfer_from: int | None = None
    transfer_to: int | None = None
    transfer_status: str
    created_at: str
    updated_at: str
    items: list[ItemInTransfer] | None = None
