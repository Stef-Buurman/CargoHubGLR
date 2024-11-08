import json
from typing import List
from models.v2.item import Item
from models.base import Base

ITEMS = []


class ItemService(Base):
    def __init__(self, root_path, is_debug=False, items=None):
        self.data_path = root_path + "items.json"
        self.load(is_debug, items)
        self.current_id = 0

    def get_items(self) -> List[Item]:
        return self.data

    def get_item(self, item_id: str) -> Item | None:
        for item in self.data:
            if item.uid == item_id:
                return item
        return None

    def get_items_for_item_line(self, item_line_id:int) -> List[Item]:
        result = []
        for x in self.data:
            if x.item_line == item_line_id:
                result.append(x)
        return result

    def get_items_for_item_group(self, item_group_id:int) -> List[Item]:
        result = []
        for x in self.data:
            if x.item_group == item_group_id:
                result.append(x)
        return result

    def get_items_for_item_type(self, item_type_id:int) -> List[Item]:
        result = []
        for x in self.data:
            if x.item_type == item_type_id:
                result.append(x)
        return result

    def get_items_for_supplier(self, supplier_id:int) -> List[Item]:
        result = []
        for x in self.data:
            if x.supplier_id == supplier_id:
                result.append(x)
        return result

    def add_item(self, item: Item) -> Item:
        item.uid = self.generate_uid()
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        self.data.append(item)
        return item

    def generate_uid(self) -> str | None:
        self.current_id = max((int(item.uid[1:]) for item in self.data), default=0)
        new_uid = None

        for _ in range(len(self.data) + 1):
            self.current_id += 1
            new_uid = f"P{self.current_id:06d}"

            if not any(item.uid == new_uid for item in self.data):
                return new_uid

        return None

    def update_item(self, item_id, item: Item) -> Item:
        item.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                self.data[i] = item
                break
        return item

    def remove_item(self, item_id):
        for x in self.data:
            if x.uid == item_id:
                self.data.remove(x)

    def load(self, is_debug: bool, items: List[Item] | None = None):
        if is_debug and items is not None:
            self.data = items
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Item(**item_dict) for item_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([item.model_dump() for item in self.data], f)
