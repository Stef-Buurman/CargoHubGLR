from models.v2.warehouse import WarehouseDB
from typing import List
from services.v2.base_service import Base
from services.v2.database_service import DB

WAREHOUSES = []


class WarehouseService(Base):
    def __init__(
        self, is_debug: bool = False, warehouses: List[WarehouseDB] | None = None
    ):
        self.db = DB
        self.load(is_debug, warehouses)

    def get_warehouses(self) -> List[WarehouseDB]:
        return self.db.get_all(WarehouseDB)

    def get_warehouse(self, warehouse_id: int) -> WarehouseDB | None:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                return warehouse
        return self.db.get(WarehouseDB, warehouse_id)

    def add_warehouse(
        self, warehouse: WarehouseDB, closeConnection: bool = True
    ) -> WarehouseDB:
        warehouse.created_at = self.get_timestamp()
        warehouse.updated_at = self.get_timestamp()
        self.data
        return self.db.insert(warehouse, closeConnection)

    def update_warehouse(
        self, warehouse_id: int, warehouse: WarehouseDB, closeConnection: bool = True
    ) -> WarehouseDB:
        warehouse.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i] = warehouse
                break
        return self.db.update(warehouse, warehouse_id, closeConnection)

    def remove_warehouse(self, warehouse_id: int, closeConnection: bool = True) -> bool:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                if self.db.delete(WarehouseDB, warehouse_id, closeConnection):
                    self.data.remove(warehouse)
                    return True
        return False

    def load(self, is_debug: bool, warehouses: List[WarehouseDB] | None = None):
        if is_debug and warehouses is not None:
            self.data = warehouses
        else:
            self.data = self.get_warehouses()
