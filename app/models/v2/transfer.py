from models.v2.base import Base2
from models.v2.ItemInObject import ItemInObject


class Transfer(Base2):
    id: int | None = None
    reference: str
    transfer_from: int | None = None
    transfer_to: int | None = None
    transfer_status: str
    created_at: str
    updated_at: str
    items: list[ItemInObject] | None = None
