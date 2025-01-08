import json
from models.v2.item_type import ItemType

from .base import Base
from services.v2 import data_provider_v2

ITEM_TYPES = []


class ItemTypes(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item_types.json"
        self.load(is_debug)

    def get_item_types(self):
        return self.data

    def get_item_type(self, item_type_id):
        for x in self.data:
            if x["id"] == item_type_id:
                return x
        return None

    def add_item_type(self, item_type):
        created_item_type = data_provider_v2.fetch_item_type_pool().add_item_type(ItemType(**item_type))
        return created_item_type.model_dump()

    def update_item_type(self, item_type_id, item_type):
        item_type["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == item_type_id:
                item_type["id"] = item_type_id
                item_type["created_at"] = self.data[i]["created_at"]
                # self.data[i] = item_type
                data_provider_v2.fetch_item_type_pool().update_item_type(item_type_id, ItemType(**item_type))
                break

    def remove_item_type(self, item_type_id):
        for x in self.data:
            if x["id"] == item_type_id:
                self.data.remove(x)
                data_provider_v2.fetch_item_type_pool().delete_item_type(item_type_id)

    def load(self, is_debug):
        if is_debug:
            self.data = ITEM_TYPES
        else:  # pragma: no cover
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data = None):  # pragma: no cover
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
