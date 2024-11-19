from models.v2.warehouse import WarehouseDB
from typing import List
from models.base import Base
from services.database_service import DB

WAREHOUSES = []


class WarehouseService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "warehouses.json"
        self.db = DB
        self.load(is_debug)

    def get_warehouses(self) -> List[WarehouseDB]:
        return self.db.get_all(WarehouseDB)

    def get_warehouse(self, warehouse_id: int) -> WarehouseDB | None:
        return self.db.get(WarehouseDB, warehouse_id)

    def add_warehouse(
        self, warehouse: WarehouseDB, closeConnection: bool = True
    ) -> WarehouseDB:
        warehouse.created_at = self.get_timestamp()
        warehouse.updated_at = self.get_timestamp()
        return self.db.insert(warehouse, closeConnection)

    def update_warehouse(
        self, warehouse_id: int, warehouse: WarehouseDB, closeConnection: bool = True
    ) -> WarehouseDB:
        warehouse.updated_at = self.get_timestamp()
        return self.db.update(warehouse, warehouse_id, closeConnection)

    def remove_warehouse(
        self, warehouse_id: int, closeConnection: bool = True
    ) -> bool:
        return self.db.delete(WarehouseDB, warehouse_id, closeConnection)

    def load(self, is_debug: bool, warehouses: List[WarehouseDB] | None = None):
        if is_debug and warehouses is not None:
            self.data = warehouses
        else:
            self.data = self.db.get_all(WarehouseDB)
