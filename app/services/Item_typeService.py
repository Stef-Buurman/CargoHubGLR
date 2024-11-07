import json
from typing import List
from models.v2.item_type import ItemType
from models.base import Base

ITEM_TYPES = []


class ItemTypeService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item_types.json"
        self.load(is_debug)

    def get_item_types(self) -> List[ItemType]:
        return self.data

    def get_item_type(self, item_type_id: int) -> ItemType | None:
        for x in self.data:
            if x.id == item_type_id:
                return x
        return None

    def add_item_type(self, item_type: ItemType) -> ItemType:
        item_type.created_at = self.get_timestamp()
        item_type.updated_at = self.get_timestamp()
        self.data.append(item_type)
        return item_type

    def update_item_type(self, item_type_id: int, item_type: ItemType) -> ItemType:
        item_type.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_type_id:
                self.data[i] = item_type
                break
        return item_type

    def remove_item_type(self, item_type_id: int) -> ItemType:
        for x in self.data:
            if x.id == item_type_id:
                self.data.remove(x)

    def load(self, is_debug: bool, item_types: List[ItemType] | None = None):
        if is_debug and item_types is not None:
            self.data = item_types
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [ItemType(**item_type_dict) for item_type_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([item_type.model_dump() for item_type in self.data], f)
