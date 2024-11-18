import json
from models.v2.supplier import Supplier
from typing import List
from models.base import Base
from services.database_service import DB

SUPPLIERS = []


class SupplierService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "suppliers.json"
        self.load(is_debug)
        self.db = DB

    def get_suppliers(self) -> List[Supplier]:
        return self.data

    def get_supplier(self, supplier_id: int) -> Supplier | None:
        for x in self.data:
            if x.id == supplier_id:
                return x
        return None

    def add_supplier(self, supplier: Supplier):
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        self.data.append(supplier)
        return supplier

    def update_supplier(self, supplier_id: int, supplier: Supplier):
        supplier.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == supplier_id:
                self.data[i] = supplier
                break
        return supplier

    def remove_supplier(self, supplier_id: int):
        for x in self.data:
            if x.id == supplier_id:
                self.data.remove(x)

    def load(self, is_debug: bool, suppliers: List[Supplier] | None = None):
        if is_debug and suppliers is not None:
            self.data = suppliers
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Supplier(**supplier_dict) for supplier_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([Supplier.model_dump() for Supplier in self.data], f)

    def insert_supplier(self, supplier: Supplier, closeConnection:bool=True) -> Supplier:
        supplier.created_at = self.get_timestamp()
        supplier.updated_at = self.get_timestamp()
        return self.db.insert(supplier, closeConnection)