import json
from models.v2.item import Item

from .base import Base
from services.v2 import data_provider_v2

ITEMS = []


class Items(Base):
    def __init__(self, root_path, is_debug=False, items=None):
        self.data_path = root_path + "items.json"
        self.is_debug = is_debug
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
        if self.is_debug:
            item["created_at"] = self.get_timestamp()
            item["updated_at"] = self.get_timestamp()
            self.data.append(item)
        else:  # pragma: no cover
            created_item = data_provider_v2.fetch_item_pool().add_item(
                Item(**item), False
            )
            return created_item.model_dump()

    def update_item(self, item_id, item):
        item["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["uid"] == item_id:
                item["uid"] = item_id
                if item.get("created_at") is None:
                    item["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = item
                    return item
                else:  # pragma: no cover
                    updated_item = data_provider_v2.fetch_item_pool().update_item(
                        item_id, Item(**item), False
                    )
                    return updated_item.model_dump()

    def remove_item(self, item_id):
        for x in self.data:
            if x["uid"] == item_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_item_pool().archive_item(item_id, False)

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
