import json
from typing import List
from models.v2.item import Item
from models.base import Base
from services.database_service import DB

ITEMS = []


class ItemService(Base):
    def __init__(self, is_debug=bool, items: List[Item] | None = None):
        self.db = D
        self.load(is_debug, items)

    def get_items(self) -> List[Item]:
        return self.db.get_all(Item)

    def get_item(self, item_id: str) -> Item | None:
        for item in self.data:
            if item.uid == item_id:
                return item
        return None

    def get_items_for_item_line(self, item_line_id: int) -> List[Item]:
        result = []
        for item in self.data:
            if item.item_line == item_line_id:
                result.append(item)
        return result

    def get_items_for_item_group(self, item_group_id: int) -> List[Item]:
        result = []
        for item in self.data:
            if item.item_group == item_group_id:
                result.append(item)
        return result

    def get_items_for_item_type(self, item_type_id: int) -> List[Item]:
        result = []
        for item in self.data:
            if item.item_type == item_type_id:
                result.append(item)
        return result

    def get_items_for_supplier(self, supplier_id: int) -> List[Item]:
        result = []
        for item in self.data:
            if item.supplier_id == supplier_id:
                result.append(item)
        return result

    def add_item(self, item: Item, closeConnection: bool = True) -> Item:
        item.uid = self.generate_uid()
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        return self.db.insert(item, closeConnection)

    def generate_uid(self) -> str | None:
        self.current_id = max((int(item.uid[1:]) for item in self.data), default=0)
        new_uid = None

        for _ in range(len(self.data) + 1):
            self.current_id += 1
            new_uid = f"P{self.current_id:06d}"

            if not any(item.uid == new_uid for item in self.data):
                return new_uid

        return None

    def update_item(
        self, item_id: int, item: Item, closeConnection: bool = True
    ) -> Item:
        item.updated_at = self.get_timestamp()
        return self.db.update(item, item_id, closeConnection)

    def remove_item(self, item_id: int, closeConnection: bool = True) -> bool:
        return self.db.delete(Item, item_id, closeConnection)

    def load(self, is_debug: bool, item: List[Item] | None = None):
        if is_debug and item is not None:
            self.data = item
        else:
            self.data = self.get_items()

    def insert_item(self, item: Item, closeConnection: bool = True) -> Item:
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        return self.db.insert(item, closeConnection)
