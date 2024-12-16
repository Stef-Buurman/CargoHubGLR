from models.v2.base import Base2
from models.v2.ItemInObject import ItemInObject


class Shipment(Base2):
    id: int | None = None
    order_id: int
    source_id: int
    order_date: str
    request_date: str
    shipment_date: str
    shipment_type: str
    shipment_status: str
    notes: str | None = None
    carrier_code: str
    carrier_description: str
    service_code: str
    payment_type: str
    transfer_mode: str
    total_package_count: int
    total_package_weight: float
    created_at: str | None = None
    updated_at: str | None = None
    items: list[ItemInObject] | None = None
