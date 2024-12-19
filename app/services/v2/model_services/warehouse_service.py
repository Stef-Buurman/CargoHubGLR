from models.v2.warehouse import Warehouse
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DB, DatabaseService

WAREHOUSES = []


class WarehouseService(Base):
    def __init__(self, db: Type[DatabaseService] = None):
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = DB
        self.load()

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
        added_warehouse = self.db.insert(warehouse, closeConnection)
        self.data.append(added_warehouse)
        return added_warehouse

    def update_warehouse(
        self, warehouse_id: int, warehouse: Warehouse, closeConnection: bool = True
    ) -> Warehouse:
        if self.is_warehouse_archived(warehouse_id):
            return None

        warehouse.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                updated_warehouse = self.db.update(
                    warehouse, warehouse_id, closeConnection
                )
                self.data[i] = updated_warehouse
                return updated_warehouse
        return None  # pragma: no cover

    def archive_warehouse(
        self, warehouse_id: int, closeConnection: bool = True
    ) -> Warehouse | None:
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_warehouse = self.db.update(
                    self.data[i], warehouse_id, closeConnection
                )
                self.data[i] = updated_warehouse
                return updated_warehouse
        return None

    def unarchive_warehouse(
        self, warehouse_id: int, closeConnection: bool = True
    ) -> Warehouse | None:
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_warehouse = self.db.update(
                    self.data[i], warehouse_id, closeConnection
                )
                self.data[i] = updated_warehouse
                return updated_warehouse
        return None

    def load(self):
        self.data = self.get_all_warehouses()

    def is_warehouse_archived(self, warehouse_id: int) -> bool:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                return warehouse.is_archived
        return None
