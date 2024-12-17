from models.v2.supplier import Supplier
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DB, DatabaseService
from services.v2 import data_provider_v2


class SupplierService(Base):
    def __init__(
        self,
        is_debug: bool = False,
        suppliers: List[Supplier] | None = None,
        db: Type[DatabaseService] = None,
    ):
        if db is not None:
            self.db = db
        else:  # pragma: no cover
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
        return None # pragma: no cover

    def archive_supplier(self, supplier_id: int, closeConnection: bool = True) -> Supplier | None:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_supplier = self.db.update(
                    self.data[i], supplier_id, closeConnection
                )
                self.data[i] = updated_supplier
                return updated_supplier
        return None

    def unarchive_supplier(
        self, supplier_id: int, closeConnection: bool = True
    ) -> Supplier | None:	
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_supplier = self.db.update(
                    self.data[i], supplier_id, closeConnection
                )
                self.data[i] = updated_supplier
                return updated_supplier
        return None

    def load(self, is_debug: bool, suppliers: List[Supplier] | None = None):
        if is_debug and suppliers is not None:
            self.data = suppliers
        else: # pragma: no cover
            self.data = self.get_all_suppliers()

    def is_supplier_archived(self, supplier_id: int) -> bool:
        for supplier in self.data:
            if supplier.id == supplier_id:
                return supplier.is_archived
        return None
