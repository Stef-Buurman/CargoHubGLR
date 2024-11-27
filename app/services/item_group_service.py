import json
from typing import List
from models.v2.item_group import ItemGroup
from models.base import Base
from services.database_service import DB
from services import data_provider_v2


class ItemGroupService(Base):
    def __init__(self, is_debug=False, item_groups: List[ItemGroup] | None = None):
        self.db = DB
        self.load(is_debug, item_groups)

    def get_item_groups(self) -> List[ItemGroup]:
        return self.db.get_all(ItemGroup)

    def get_item_group(self, item_group_id: int) -> ItemGroup:
        for item_group in self.data:
            if item_group.id == item_group_id:
                return item_group
        return None

    def add_item_group(
        self, item_group: ItemGroup, closeConnection: bool = True
    ) -> ItemGroup:
        item_group.created_at = self.get_timestamp()
        item_group.updated_at = self.get_timestamp()
        self.data.append(item_group)
        return self.db.insert(item_group, closeConnection)

    def update_item_group(
        self, item_group_id: int, item_group: ItemGroup, closeConnection: bool = True
    ) -> ItemGroup:
        item_group.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_group_id:
                self.data[i] = item_group
                break
        return self.db.update(item_group, item_group_id, closeConnection)

    def remove_item_group(self, item_group_id: int, closeConnection: bool = True):
        if (
            len(
                data_provider_v2.fetch_item_pool().get_items_for_item_group(
                    item_group_id
                )
            )
            > 0
        ):
            return False
        for item_group in self.data:
            if item_group.id == item_group_id:
                if self.db.delete(ItemGroup, item_group_id, closeConnection):
                    self.data.remove(item_group)
                    return True
        return False

    def load(self, is_debug: bool, item_groups: List[ItemGroup] | None = None):
        if is_debug and item_groups is not None:
            self.data = item_groups
        else:
            self.data = self.get_item_groups()
