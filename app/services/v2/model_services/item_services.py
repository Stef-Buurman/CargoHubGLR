from typing import List
from models.v2.item import Item
from services.v2.base_service import Base
from services.v2.database_service import DB
from services.v2 import data_provider_v2


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

    def has_item_archived_entities(self, item: Item) -> bool:
        if (
            item.item_group is not None
            and data_provider_v2.fetch_item_group_pool().is_item_group_archived(
                item.item_group
            )
        ):
            return True
        elif (
            item.item_line is not None
            and data_provider_v2.fetch_item_line_pool().is_item_line_archived(
                item.item_line
            )
        ):
            return True
        elif (
            item.item_type is not None
            and data_provider_v2.fetch_item_type_pool().is_item_type_archived(
                item.item_type
            )
        ):
            return True
        return False

    def add_item(self, item: Item, closeConnection: bool = True) -> Item | None:
        if self.has_item_archived_entities(item):
            return None
        item.uid = self.generate_uid()
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        added_item = self.db.insert(item, closeConnection)
        self.data.append(added_item)
        return added_item

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
        self, item_id: str, item: Item, closeConnection: bool = True
    ) -> Item | None:
        if self.is_item_archived(item_id) or self.has_item_archived_entities(item):
            return None

        item.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].uid == item.uid:
                updated_item = self.db.update(item, item_id, closeConnection)
                self.data[i] = updated_item
                return updated_item
        return None

    def is_item_archived(self, item_id: str) -> bool | None:
        for item in self.data:
            if item.uid == item_id:
                return item.is_archived
        return None

    def archive_item(self, item_id: str, closeConnection: bool = True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                updated_item = self.db.update(self.data[i], item_id, closeConnection)
                self.data[i] = updated_item
                return updated_item
        return None

    def unarchive_item(self, item_id: str, closeConnection: bool = True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                self.data[i].is_archived = False
                self.data[i].updated_at = self.get_timestamp()
                updated_item = self.db.update(self.data[i], item_id, closeConnection)
                self.data[i] = updated_item
                return updated_item
        return None

    def load(self, is_debug: bool, item: List[Item] | None = None):
        if is_debug and item is not None:
            self.data = item
        else:
            self.data = self.get_all_items()
