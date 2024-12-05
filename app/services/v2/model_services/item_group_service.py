from typing import List
from models.v2.item_group import ItemGroup
from services.v2.base_service import Base
from services.v2.database_service import DB
from services.v2 import data_provider_v2


class ItemGroupService(Base):
    def __init__(self, is_debug=False, item_groups: List[ItemGroup] | None = None):
        self.db = DB
        self.load(is_debug, item_groups)

    def get_all_item_groups(self) -> List[ItemGroup]:
        return self.db.get_all(ItemGroup)

    def get_item_groups(self) -> List[ItemGroup]:
        item_groups = []
        for item_group in self.data:
            if not item_group.is_archived:
                item_groups.append(item_group)
        return item_groups

    def get_item_group(self, item_group_id: int) -> ItemGroup:
        for item_group in self.data:
            if item_group.id == item_group_id:
                return item_group
        return self.db.get(ItemGroup, item_group_id)

    def is_item_group_archived(self, item_group_id: int) -> bool:
        for item_group in self.data:
            if item_group.id == item_group_id:
                return item_group.is_archived
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
        if self.is_item_group_archived(item_group_id):
            return None

        item_group.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_group_id:
                self.data[i] = item_group
                break
        return self.db.update(item_group, item_group_id, closeConnection)

    def archive_item_group(self, item_group_id: int, closeConnection: bool = True) -> ItemGroup | None:
        for item_group in self.data:
            if item_group.id == item_group_id:
                item_group.is_archived = True
                item_group.updated_at = self.get_timestamp()
                return self.db.update(item_group, item_group_id, closeConnection)
        return None
    

    def unarchive_item_group(self, item_group_id: int, closeConnection: bool = True) -> ItemGroup | None:
        for item_group in self.data:
            if item_group.id == item_group_id:
                item_group.is_archived = False
                item_group.updated_at = self.get_timestamp()
                return self.db.update(item_group, item_group_id, closeConnection)
        return None
            

    def load(self, is_debug: bool, item_groups: List[ItemGroup] | None = None):
        if is_debug and item_groups is not None:
            self.data = item_groups
        else:
            self.data = self.get_all_item_groups()
