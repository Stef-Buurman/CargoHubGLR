from typing import List
from models.v2.item_type import ItemType
from services.v2.base_service import Base
from services.v2.database_service import DB
from services.v2 import data_provider_v2


class ItemTypeService(Base):
    def __init__(self, is_debug=False, item_types: List[ItemType] | None = None):
        self.db = DB
        self.load(is_debug, item_types)

    def get_item_types(self) -> List[ItemType]:
        return self.db.get_all(ItemType)

    def get_item_type(self, item_type_id: int) -> ItemType | None:
        for item_type in self.data:
            if item_type.id == item_type_id:
                return item_type
        return self.db.get(ItemType, item_type_id)

    def add_item_type(
        self, item_type: ItemType, closeConnection: bool = True
    ) -> ItemType:
        item_type.created_at = self.get_timestamp()
        item_type.updated_at = self.get_timestamp()
        self.data.append(item_type)
        return self.db.insert(item_type, closeConnection)

    def update_item_type(
        self, item_type_id: int, item_type: ItemType, closeConnection: bool = True
    ) -> ItemType:
        item_type.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_type_id:
                self.data[i] = item_type
                break
        return self.db.update(item_type, item_type_id, closeConnection)

    def remove_item_type(self, item_type_id: int, closeConnection: bool = True) -> bool:
        if (
            len(
                data_provider_v2.fetch_item_pool().get_items_for_item_type(item_type_id)
            )
            > 0
        ):
            return False
        for item_type in self.data:
            if item_type.id == item_type_id:
                if self.db.delete(ItemType, item_type_id, closeConnection):
                    self.data.remove(item_type)
                    return True
        return False

    def load(self, is_debug: bool, item_types: List[ItemType] | None = None):
        if is_debug and item_types is not None:
            self.data = item_types
        else:
            self.data = self.get_item_types()
