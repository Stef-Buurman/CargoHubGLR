from services.v2 import data_provider_v2
from models.v2.supplier import Supplier
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DB, DatabaseService
from services.v1 import data_provider


class SupplierService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = DB
        self.load()

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

    def add_supplier(self, supplier: Supplier) -> Supplier:
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        added_supplier = self.db.insert(supplier)
        self.data.append(added_supplier)
        self.save()
        return added_supplier

    def update_supplier(self, supplier_id: int, supplier: Supplier):
        if self.is_supplier_archived(supplier_id):
            return None

        supplier.updated_at = self.get_timestamp()

        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                updated_supplier = self.db.update(supplier, supplier_id)
                self.data[i] = updated_supplier
                self.save()
                return updated_supplier
        return None  # pragma: no cover

    def archive_supplier(self, supplier_id: int) -> Supplier | None:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_supplier = self.db.update(self.data[i], supplier_id)
                self.data[i] = updated_supplier
                self.save()
                return updated_supplier
        return None

    def unarchive_supplier(self, supplier_id: int) -> Supplier | None:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_supplier = self.db.update(self.data[i], supplier_id)
                self.data[i] = updated_supplier
                self.save()
                return updated_supplier
        return None

    def save(self):
        if not self.is_debug:
            data_provider_v2.fetch_background_tasks().add_task(
                data_provider.fetch_supplier_pool().save(
                    [supplier.model_dump() for supplier in self.data]
                )
            )

    def load(self):
        self.data = self.get_all_suppliers()

    def is_supplier_archived(self, supplier_id: int) -> bool:
        for supplier in self.data:
            if supplier.id == supplier_id:
                return supplier.is_archived
        return None
