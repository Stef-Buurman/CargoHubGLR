from models.v2.supplier import Supplier
from typing import List
from models.base import Base
from services.database_service import DB

SUPPLIERS = []


class SupplierService(Base):
    def __init__(self, is_debug: bool = False, suppliers: List[Supplier] | None = None):
        self.db = DB
        self.load(is_debug, suppliers)

    def get_suppliers(self) -> List[Supplier]:
        return self.db.get_all(Supplier)

    def get_supplier(self, supplier_id: int) -> Supplier | None:
        for supplier in self.data:
            if supplier.id == supplier_id:
                return supplier
        return None

    def add_supplier(
        self, supplier: Supplier, closeConnection: bool = True
    ) -> Supplier:
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        return self.db.insert(supplier, closeConnection)

    def update_supplier(
        self, supplier_id: int, supplier: Supplier, closeConnection: bool = True
    ):
        supplier.updated_at = self.get_timestamp()
        return self.db.update(supplier, supplier_id, closeConnection)

    def remove_supplier(self, supplier_id: int):
        return self.db.delete(Supplier, supplier_id)

    def load(self, is_debug: bool, suppliers: List[Supplier] | None = None):
        if is_debug and suppliers is not None:
            self.data = suppliers
        else:
            self.data = self.get_suppliers()
