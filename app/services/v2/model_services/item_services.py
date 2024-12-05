from typing import List
from models.v2.item import Item
from services.v2.base_service import Base
from services.v2.database_service import DB


class ItemService(Base):
    def __init__(self, is_debug=bool, items: List[Item] | None = None):
        self.db = DB
        self.load(is_debug, items)

    def get_all_items(self) -> List[Item]:
        return self.db.get_all(Item)

    def get_items(self) -> List[Item]:
        items = []
        for item in self.data:
            if not item.is_archived:
                items.append(item)
        return items

    def get_item(self, item_id: str) -> Item | None:
        for item in self.data:
            if item.uid == item_id:
                return item
        return self.db.get(Item, item_id)

    def get_items_for_item_line(self, item_line_id: int) -> List[Item]:
        result = []
        for item in self.get_items():
            if item.item_line == item_line_id:
                result.append(item)
        return result

    def get_items_for_item_group(self, item_group_id: int) -> List[Item]:
        result = []
        for item in self.get_items():
            if item.item_group == item_group_id:
                result.append(item)
        return result

    def get_items_for_item_type(self, item_type_id: int) -> List[Item]:
        result = []
        for item in self.get_items():
            if item.item_type == item_type_id:
                result.append(item)
        return result

    def get_items_for_supplier(self, supplier_id: int) -> List[Item]:
        result = []
        for item in self.get_items():
            if item.supplier_id == supplier_id:
                result.append(item)
        return result

    def add_item(self, item: Item, closeConnection: bool = True) -> Item:
        item.uid = self.generate_uid()
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        self.data.append(item)
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
    ) -> Item | None:
        if self.is_item_archived(item_id):
            return None

        item.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].uid == item.uid:
                self.data[i] = item
                break
        return self.db.update(item, item_id, closeConnection)

    def is_item_archived(self, item_id: int) -> bool | None:
        for item in self.data:
            if item.uid == item_id:
                return item.is_archived
        return None

    def archive_item(self, item_id: int, closeConnection: bool = True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                return self.db.update(self.data[i], item_id, closeConnection)
        return None

    def unarchive_item(self, item_id: int, closeConnection: bool = True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                self.data[i].is_archived = False
                self.data[i].updated_at = self.get_timestamp()
                return self.db.update(self.data[i], item_id, closeConnection)
        return None

    def load(self, is_debug: bool, item: List[Item] | None = None):
        if is_debug and item is not None:
            self.data = item
        else:
            self.data = self.get_all_items()
