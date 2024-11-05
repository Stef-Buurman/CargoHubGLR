import json
from models.v2.warehouse import Warehouse
from typing import List
from models.base import Base

WAREHOUSES = []


class WarehouseService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "warehouses.json"
        self.load(is_debug)

    def get_warehouses(self) -> List[Warehouse]:
        return self.data

    def get_warehouse(self, warehouse_id: int) -> Warehouse | None:
        for x in self.data:
            if x.id == warehouse_id:
                return x
        return None

    def add_warehouse(self, warehouse: Warehouse):
        warehouse.created_at = self.get_timestamp()
        warehouse.updated_at = self.get_timestamp()
        self.data.append(warehouse)

    def update_warehouse(self, warehouse_id: int, warehouse: Warehouse):
        warehouse.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i] = warehouse
                break

    def remove_warehouse(self, warehouse_id: int):
        for x in self.data:
            if x.id == warehouse_id:
                self.data.remove(x)

    def load(self, is_debug: bool, warehouses: List[Warehouse] | None = None):
        if is_debug and warehouses is not None:
            self.data = warehouses
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Warehouse(**warehouse_dict) for warehouse_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([warehouse.model_dump() for warehouse in self.data], f)
