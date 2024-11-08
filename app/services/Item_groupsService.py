import json
from typing import List
from models.v2.item_group import ItemGroup
from models.base import Base

ITEM_GROUPS = []


class ItemGroupService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item_groups.json"
        self.load(is_debug)

    def get_item_groups(self)-> List[ItemGroup]:
        return self.data

    def get_item_group(self, item_group_id:int) -> ItemGroup:
        for x in self.data:
            if x.id == item_group_id:
                return x
        return None

    def add_item_group(self, item_group:ItemGroup) -> ItemGroup:
        item_group.created_at = self.get_timestamp()
        item_group.updated_at = self.get_timestamp()
        self.data.append(item_group)
        return item_group

    def update_item_group(self, item_group_id:int, item_group:ItemGroup) -> ItemGroup:
        item_group.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_group_id:
                self.data[i] = item_group
                break
        return item_group

    def remove_item_group(self, item_group_id:int):
        for x in self.data:
            if x.id == item_group_id:
                self.data.remove(x)

    def load(self, is_debug: bool, item_groups: List[ItemGroup] | None = None):
        if is_debug and item_groups is not None:
            self.data = item_groups
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [
                    ItemGroup(**item_group_dict) for item_group_dict in raw_data
                ]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([item_group.model_dump() for item_group in self.data], f)
