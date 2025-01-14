from typing import List, Type
from services.v2 import data_provider_v2
from models.v2.item_type import ItemType
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class ItemTypeService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = data_provider_v2.fetch_database()
        self.load()

    def get_all_item_types(self) -> List[ItemType]:
        return self.db.get_all(ItemType)

    def get_item_types(self) -> List[ItemType]:
        item_types = []
        for item_type in self.data:
            if not item_type.is_archived:
                item_types.append(item_type)
        return item_types

    def get_item_type(self, item_type_id: int) -> ItemType | None:
        for item_type in self.data:
            if item_type.id == item_type_id:
                return item_type
        return self.db.get(ItemType, item_type_id)

    def add_item_type(self, item_type: ItemType) -> ItemType:
        item_type.created_at = self.get_timestamp()
        item_type.updated_at = self.get_timestamp()
        added_item_type = self.db.insert(item_type)
        self.data.append(added_item_type)
        self.save()
        return added_item_type

    def update_item_type(self, item_type_id: int, item_type: ItemType) -> ItemType:
        if self.is_item_type_archived(item_type_id):
            return None

        item_type.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_type_id:
                updae_item_type = self.db.update(item_type, item_type_id)
                self.data[i] = updae_item_type
                self.save()
                return updae_item_type
        return None  # pragma: no cover

    def is_item_type_archived(self, item_type_id: int) -> bool:
        for item_type in self.data:
            if item_type.id == item_type_id:
                return item_type.is_archived
        return None

    def archive_item_type(self, item_type_id: int) -> ItemType | None:
        for i in range(len(self.data)):
            if self.data[i].id == item_type_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                updated_item_type = self.db.update(self.data[i], item_type_id)
                self.data[i] = updated_item_type
                self.save()
                return updated_item_type
        return None

    def unarchive_item_type(self, item_type_id: int) -> ItemType | None:
        for i in range(len(self.data)):
            if self.data[i].id == item_type_id:
                self.data[i].is_archived = False
                updated_item_type = self.db.update(self.data[i], item_type_id)
                self.data[i] = updated_item_type
                self.save()
                return updated_item_type
        return None

    def save(self):
        if not self.is_debug:
            data_provider_v2.fetch_background_tasks().add_task(
                data_provider.fetch_item_type_pool().save(
                    [item.model_dump() for item in self.data]
                )
            )

    def load(self):
        self.data = self.get_all_item_types()
