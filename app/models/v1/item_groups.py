import json
from models.v2.item_group import ItemGroup

from .base import Base
from services.v2 import data_provider_v2

ITEM_GROUPS = []


class ItemGroups(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "item_groups.json"
        self.load(is_debug)

    def get_item_groups(self):
        return self.data

    def get_item_group(self, item_group_id):
        for x in self.data:
            if x["id"] == item_group_id:
                return x
        return None

    def add_item_group(self, item_group):
        if self.is_debug:
            item_group["created_at"] = self.get_timestamp()
            item_group["updated_at"] = self.get_timestamp()
            self.data.append(item_group)
            return item_group
        else:
            added_item_group = data_provider_v2.fetch_item_group_pool().add_item_group(
                ItemGroup(**item_group)
            )
            return added_item_group.model_dump()

    def update_item_group(self, item_group_id, item_group):
        item_group["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == item_group_id:
                item_group["id"] = item_group_id
                if item_group.get("created_at") is None:
                    item_group["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = item_group
                    return item_group
                else:
                    updated_item_group = (
                        data_provider_v2.fetch_item_group_pool().update_item_group(
                            item_group_id, ItemGroup(**item_group)
                        )
                    )
                    return updated_item_group.model_dump()

    def remove_item_group(self, item_group_id):
        for x in self.data:
            if x["id"] == item_group_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_item_group_pool().archive_item_group(
                        item_group_id
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = ITEM_GROUPS
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
