from models.v2.base import BaseWithArchived
from models.v2.ItemInObject import ItemInObject


class Transfer(BaseWithArchived):
    id: int | None = None
    reference: str
    transfer_from: int | None = None
    transfer_to: int | None = None
    transfer_status: str
    created_at: str
    updated_at: str
    items: list[ItemInObject] | None = None
