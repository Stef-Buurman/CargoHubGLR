import json
from models.v2.item import Item

from .base import Base
from services.v2 import data_provider_v2

ITEMS = []


class Items(Base):
    def __init__(self, root_path, is_debug=False, items=None):
        self.data_path = root_path + "items.json"
        self.load(is_debug, items)

    def get_items(self):
        return self.data

    def get_item(self, item_id):
        for x in self.data:
            if x["uid"] == item_id:
                return x
        return None

    def get_items_for_item_line(self, item_line_id):
        result = []
        for x in self.data:
            if x["item_line"] == item_line_id:
                result.append(x)
        return result

    def get_items_for_item_group(self, item_group_id):
        result = []
        for x in self.data:
            if x["item_group"] == item_group_id:
                result.append(x)
        return result

    def get_items_for_item_type(self, item_type_id):
        result = []
        for x in self.data:
            if x["item_type"] == item_type_id:
                result.append(x)
        return result

    def get_items_for_supplier(self, supplier_id):
        result = []
        for x in self.data:
            if x["supplier_id"] == supplier_id:
                result.append(x)
        return result

    def add_item(self, item):
        created_item = data_provider_v2.fetch_item_pool().add_item(Item(**item))
        return created_item.model_dump()

    def update_item(self, item_id, item):
        item["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["uid"] == item_id:
                item["uid"] = item_id
                item["created_at"] = self.data[i]["created_at"]
                updated_item = data_provider_v2.fetch_item_pool().update_item(
                    item_id, Item(**item)
                )
                return updated_item.model_dump()

    def remove_item(self, item_id):
        for x in self.data:
            if x["uid"] == item_id:
                self.data.remove(x)
                data_provider_v2.fetch_item_pool().delete_item(item_id)

    def load(self, is_debug, items):
        if is_debug:
            self.data = items
        else:  # pragma: no cover
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):  # pragma: no cover
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
