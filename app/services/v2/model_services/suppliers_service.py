from models.v2.supplier import Supplier
from typing import List
from services.v2.base_service import Base
from services.v2.database_service import DB
from services.v2 import data_provider_v2


class SupplierService(Base):
    def __init__(self, is_debug: bool = False, suppliers: List[Supplier] | None = None):
        self.db = DB
        self.load(is_debug, suppliers)

    def get_all_suppliers(self) -> List[Supplier]:
        return self.db.get_all(Supplier)

    def get_suppliers(self) -> List[Supplier]:
        suppliers = []
        for supplier in self.data:
            if not supplier.is_archived:
                suppliers.append(supplier)
        return suppliers

    def get_supplier(self, supplier_id: int) -> Supplier | None:
        for supplier in self.data:
            if supplier.id == supplier_id:
                if supplier.is_archived:
                    return None
                return supplier
        return self.db.get(Supplier, supplier_id)

    def add_supplier(
        self, supplier: Supplier, closeConnection: bool = True
    ) -> Supplier:
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        added_supplier = self.db.insert(supplier, closeConnection)
        self.data.append(added_supplier)
        return added_supplier

    def update_supplier(
        self, supplier_id: int, supplier: Supplier, closeConnection: bool = True
    ):
        if self.is_supplier_archived(supplier_id):
            return None

        supplier.updated_at = self.get_timestamp()

        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                updated_supplier = self.db.update(
                    supplier, supplier_id, closeConnection
                )
                self.data[i] = updated_supplier
                return updated_supplier
        return None

    def archive_supplier(self, supplier_id: int, closeConnection: bool = True) -> bool:
        if (
            len(data_provider_v2.fetch_item_pool().get_items_for_supplier(supplier_id))
            > 0
        ):
            return False
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_supplier = self.db.update(
                    self.data[i], supplier_id, closeConnection
                )
                self.data[i] = updated_supplier
                return True
        return False

    def unarchive_supplier(
        self, supplier_id: int, closeConnection: bool = True
    ) -> bool:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_supplier = self.db.update(
                    self.data[i], supplier_id, closeConnection
                )
                self.data[i] = updated_supplier
                return True
        return False

    def load(self, is_debug: bool, suppliers: List[Supplier] | None = None):
        if is_debug and suppliers is not None:
            self.data = suppliers
        else:
            self.data = self.get_all_suppliers()

    def is_supplier_archived(self, supplier_id: int) -> bool:
        for supplier in self.data:
            if supplier.id == supplier_id:
                return supplier.is_archived
        return None
