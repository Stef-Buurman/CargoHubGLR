from typing import List
from .ItemInObject import ItemInObject
from models.v2.base import Base

class Order(Base):
    id: int | None = None
    source_id: int
    order_date: str
    request_date: str
    reference: str
    reference_extra: str
    order_status: str
    notes: str
    shipping_notes: str
    picking_notes: str
    warehouse_id: int
    ship_to: int | None
    bill_to: int | None
    shipment_id: int
    total_amount: float
    total_discount: float
    total_tax: float
    total_surcharge: float
    created_at: str | None = None
    updated_at: str | None = None
    items: List[ItemInObject] | None = None
