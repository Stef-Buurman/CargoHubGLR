from pydantic import ConfigDict
from models.v2.base import Base


class Item(Base):
    uid: str | None = None
    code: str
    description: str
    short_description: str
    upc_code: str
    model_number: str
    commodity_code: str
    item_line: int
    item_group: int
    item_type: int
    unit_purchase_quantity: int
    unit_order_quantity: int
    pack_order_quantity: int
    supplier_id: int
    supplier_code: str
    supplier_part_number: str
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(protected_namespaces=())
