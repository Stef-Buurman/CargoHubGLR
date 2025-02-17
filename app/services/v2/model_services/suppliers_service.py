import threading
from services.v2 import data_provider_v2
from models.v2.supplier import Supplier
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class SupplierService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()
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

    def add_supplier(self, supplier: Supplier, background_task=True) -> Supplier:
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        added_supplier = self.db.insert(supplier)
        self.data.append(added_supplier)
        self.save(background_task)
        return added_supplier

    def update_supplier(
        self, supplier_id: int, supplier: Supplier, background_task=True
    ):
        if self.is_supplier_archived(supplier_id):
            return None

        supplier.updated_at = self.get_timestamp()

        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                updated_supplier = self.db.update(supplier, supplier_id)
                self.data[i] = updated_supplier
                self.save(background_task)
                return updated_supplier
        return None

    def archive_supplier(
        self, supplier_id: int, background_task=True
    ) -> Supplier | None:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_supplier = self.db.update(self.data[i], supplier_id)
                self.data[i] = updated_supplier
                self.save(background_task)
                return updated_supplier
        return None

    def unarchive_supplier(
        self, supplier_id: int, background_task=True
    ) -> Supplier | None:
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_supplier = self.db.update(self.data[i], supplier_id)
                self.data[i] = updated_supplier
                self.save(background_task)
                return updated_supplier
        return None

    def save(self, background_task=True):  # pragma: no cover:
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_supplier_pool().save(
                    [shipment.model_dump() for shipment in self.data]
                )

            if background_task:
                threading.Thread(target=call_v1_save_method).start()
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_suppliers()

    def is_supplier_archived(self, supplier_id: int) -> bool:
        for supplier in self.data:
            if supplier.id == supplier_id:
                return supplier.is_archived
        return None
