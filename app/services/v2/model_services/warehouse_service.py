from services.v2 import data_provider_v2
from models.v2.warehouse import Warehouse
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class WarehouseService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = data_provider_v2.fetch_database()
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

    def add_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.created_at = self.get_timestamp()
        warehouse.updated_at = self.get_timestamp()
        added_warehouse = self.db.insert(warehouse)
        self.data.append(added_warehouse)
        self.save()
        return added_warehouse

    def update_warehouse(
        self, warehouse_id: int, warehouse: Warehouse
    ) -> Warehouse | None:
        if self.is_warehouse_archived(warehouse_id):
            return None

        warehouse.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                warehouse.id = warehouse_id
                if warehouse.created_at is None:
                    warehouse.created_at = self.data[i].created_at
                updated_warehouse = self.db.update(warehouse, warehouse_id)
                self.data[i] = updated_warehouse
                self.save()
                return updated_warehouse
        return None  # pragma: no cover

    def archive_warehouse(self, warehouse_id: int) -> Warehouse | None:
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_warehouse = self.db.update(self.data[i], warehouse_id)
                self.data[i] = updated_warehouse
                self.save()
                return updated_warehouse
        return None

    def unarchive_warehouse(self, warehouse_id: int) -> Warehouse | None:
        for i in range(len(self.data)):
            if self.data[i].id == warehouse_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_warehouse = self.db.update(self.data[i], warehouse_id)
                self.data[i] = updated_warehouse
                self.save()
                return updated_warehouse
        return None

    def save(self):
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_shipment_pool().save(
                    [shipment.model_dump() for shipment in self.data]
                )

            data_provider_v2.fetch_background_tasks().add_task(call_v1_save_method)

    def load(self):
        self.data = self.get_all_warehouses()

    def is_warehouse_archived(self, warehouse_id: int) -> bool | None:
        for warehouse in self.data:
            if warehouse.id == warehouse_id:
                return warehouse.is_archived
        return None
