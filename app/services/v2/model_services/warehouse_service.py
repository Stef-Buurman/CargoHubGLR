from models.v2.warehouse import Warehouse
from typing import List
from services.v2.base_service import Base
from services.v2.database_service import DB

WAREHOUSES = []


class WarehouseService(Base):
    def __init__(
        self, is_debug: bool = False, warehouses: List[Warehouse] | None = None
    ):
        self.db = DB
        self.load(is_debug, warehouses)

    def get_all_warehouses(self) -> List[Warehouse]:
        return self.db.get_all(Warehouse)

    def get_warehouses(self) -> List[Warehouse]:
        warehouses = []
        for warehouse in self.data:
            if not warehouse.is_archived:
                warehouses.append(warehouse)
        return warehouses

    def get_warehouse(self, warehouse_id: int) -> Warehouse | None:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                return warehouse
        return self.db.get(Warehouse, warehouse_id)

    def add_warehouse(
        self, warehouse: Warehouse, closeConnection: bool = True
    ) -> Warehouse:
        warehouse.created_at = self.get_timestamp()
        warehouse.updated_at = self.get_timestamp()
        self.data
        return self.db.insert(warehouse, closeConnection)

    def update_warehouse(
        self, warehouse_id: int, warehouse: Warehouse, closeConnection: bool = True
    ) -> Warehouse:
        warehouse.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                if self.data[i].is_archived:
                    return None
                self.data[i] = warehouse
                break
        return self.db.update(warehouse, warehouse_id, closeConnection)

    def archive_warehouse(
        self, warehouse_id: int, closeConnection: bool = True
    ) -> bool:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                warehouse.updated_at = self.get_timestamp()
                warehouse.is_archived = True
                if self.db.update(warehouse, warehouse_id, closeConnection):
                    return True
        return False

    def unarchive_warehouse(
        self, warehouse_id: int, closeConnection: bool = True
    ) -> bool:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                warehouse.updated_at = self.get_timestamp()
                warehouse.is_archived = False
                if self.db.update(warehouse, warehouse_id, closeConnection):
                    return True
        return False

    def load(self, is_debug: bool, warehouses: List[Warehouse] | None = None):
        if is_debug and warehouses is not None:
            self.data = warehouses
        else:
            self.data = self.get_all_warehouses()

    def is_warehouse_archived(self, warehouse_id: int) -> bool:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                return warehouse.is_archived
        return None
