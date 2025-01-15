import json
from models.v2.warehouse import Warehouse

from .base import Base
from services.v2 import data_provider_v2

WAREHOUSES = []


class Warehouses(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "warehouses.json"
        self.load(is_debug)

    def get_warehouses(self):
        return self.data

    def get_warehouse(self, warehouse_id):
        for x in self.data:
            if x["id"] == warehouse_id:
                return x
        return None

    def add_warehouse(self, warehouse):
        if self.is_debug:
            warehouse["created_at"] = self.get_timestamp()
            warehouse["updated_at"] = self.get_timestamp()
            self.data.append(warehouse)
            return warehouse
        else:
            created_warehouse = data_provider_v2.fetch_warehouse_pool().add_warehouse(
                Warehouse(**warehouse), False
            )
            return created_warehouse.model_dump()

    def update_warehouse(self, warehouse_id, warehouse):
        warehouse["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == warehouse_id:
                warehouse["id"] = warehouse_id
                if warehouse.get("created_at") is None:
                    warehouse["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = warehouse
                    return warehouse
                else:
                    updated_warehouse = (
                        data_provider_v2.fetch_warehouse_pool().update_warehouse(
                            warehouse_id, Warehouse(**warehouse), False
                        )
                    )
                    return updated_warehouse.model_dump()

    def remove_warehouse(self, warehouse_id):
        for x in self.data:
            if x["id"] == warehouse_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_warehouse_pool().archive_warehouse(
                        warehouse_id, False
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = WAREHOUSES
        else:  # pragma: no cover
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):  # pragma: no cover
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
