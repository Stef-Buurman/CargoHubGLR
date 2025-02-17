import threading
from typing import List, Type
from models.v2.item import Item
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v2 import data_provider_v2
from services.v1 import data_provider


class ItemService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()
        self.load()

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

    def has_item_archived_entities(
        self, new_item: Item, old_item: Item | None = None
    ) -> bool:
        if old_item is not None:
            if (
                new_item.item_group is not None
                and new_item.item_group != old_item.item_group
                and data_provider_v2.fetch_item_group_pool().is_item_group_archived(
                    new_item.item_group
                )
            ):
                return True
            elif (
                new_item.item_line is not None
                and new_item.item_line != old_item.item_line
                and data_provider_v2.fetch_item_line_pool().is_item_line_archived(
                    new_item.item_line
                )
            ):
                return True
            elif (
                new_item.item_type is not None
                and new_item.item_type != old_item.item_type
                and data_provider_v2.fetch_item_type_pool().is_item_type_archived(
                    new_item.item_type
                )
            ):
                return True
            elif (
                new_item.supplier_id is not None
                and new_item.supplier_id != old_item.supplier_id
                and data_provider_v2.fetch_supplier_pool().is_supplier_archived(
                    new_item.supplier_id
                )
            ):
                return True
        else:
            if (
                new_item.item_group is not None
                and data_provider_v2.fetch_item_group_pool().is_item_group_archived(
                    new_item.item_group
                )
            ):
                return True
            elif (
                new_item.item_line is not None
                and data_provider_v2.fetch_item_line_pool().is_item_line_archived(
                    new_item.item_line
                )
            ):
                return True
            elif (
                new_item.item_type is not None
                and data_provider_v2.fetch_item_type_pool().is_item_type_archived(
                    new_item.item_type
                )
            ):
                return True
            elif (
                new_item.supplier_id is not None
                and data_provider_v2.fetch_supplier_pool().is_supplier_archived(
                    new_item.supplier_id
                )
            ):
                return True
        return False

    def add_item(self, item: Item, background_task=True) -> Item | None:
        if self.has_item_archived_entities(item):
            return None
        item.uid = self.generate_uid()
        item.created_at = self.get_timestamp()
        item.updated_at = self.get_timestamp()
        added_item = self.db.insert(item)
        self.data.append(added_item)
        self.save(background_task)
        return added_item

    def generate_uid(self) -> str:
        existing_ids = (int(item.uid[1:]) for item in self.data if hasattr(item, "uid"))
        current_id = max(existing_ids, default=0) + 1

        while f"P{current_id:06d}" in existing_ids:
            current_id += 1

        return f"P{current_id:06d}"

    def update_item(
        self, item_id: str, item: Item, background_task=True
    ) -> Item | None:
        old_item = self.get_item(item_id)
        if self.is_item_archived(
            item_id
        ) is not False or self.has_item_archived_entities(item, old_item):
            return None

        item.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                item.uid = item_id
                item.created_at = self.data[i].created_at
                updated_item = self.db.update(item, item_id)
                self.data[i] = updated_item
                self.save(background_task)
                return updated_item
        return None

    def is_item_archived(self, item_id: str) -> bool | None:
        for item in self.data:
            if item.uid == item_id:
                return item.is_archived
        return None

    def archive_item(self, item_id: str, background_task=True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                new_item = self.data[i].model_copy()
                new_item.is_archived = True
                new_item.updated_at = self.get_timestamp()
                updated_item = self.db.update(new_item, item_id)
                self.data[i] = updated_item
                self.save(background_task)
                return updated_item
        return None

    def unarchive_item(self, item_id: str, background_task=True) -> Item | None:
        for i in range(len(self.data)):
            if self.data[i].uid == item_id:
                new_item = self.data[i].model_copy()
                new_item.is_archived = False
                new_item.updated_at = self.get_timestamp()
                updated_item = self.db.update(new_item, item_id)
                self.data[i] = updated_item
                self.save(background_task)
                return updated_item
        return None

    def save(self, background_task=True):  # pragma: no cover:
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_item_pool().save(
                    [item.model_dump() for item in self.data]
                )

            if background_task:
                threading.Thread(target=call_v1_save_method).start()
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_items()
