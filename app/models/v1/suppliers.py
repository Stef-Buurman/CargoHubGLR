import json
from models.v2.supplier import Supplier

from .base import Base
from services.v2 import data_provider_v2

SUPPLIERS = []


class Suppliers(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "suppliers.json"
        self.load(is_debug)

    def get_suppliers(self):
        return self.data

    def get_supplier(self, supplier_id):
        for x in self.data:
            if x["id"] == supplier_id:
                return x
        return None

    def add_supplier(self, supplier):
        if self.is_debug:
            supplier["created_at"] = self.get_timestamp()
            supplier["updated_at"] = self.get_timestamp()
            self.data.append(supplier)
            return supplier
        else:
            created_client = data_provider_v2.fetch_supplier_pool().add_supplier(
                Supplier(**supplier), False
            )
            return created_client.model_dump()

    def update_supplier(self, supplier_id, supplier):
        supplier["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == supplier_id:
                supplier["id"] = supplier_id
                if supplier.get("created_at") is None:
                    supplier["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = supplier
                    return supplier
                else:
                    updated_supplier = (
                        data_provider_v2.fetch_supplier_pool().update_supplier(
                            supplier_id, Supplier(**supplier), False
                        )
                    )
                    return updated_supplier.model_dump()

    def remove_supplier(self, supplier_id):
        for x in self.data:
            if x["id"] == supplier_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_supplier_pool().archive_supplier(
                        supplier_id, False
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = SUPPLIERS
        else:
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
