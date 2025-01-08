import json
from models.v2.item_line import ItemLine
from .base import Base
from services.v2 import data_provider_v2

ITEM_LINES = []


class ItemLines(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "item_lines.json"
        self.load(is_debug)

    def get_item_lines(self):
        return self.data

    def get_item_line(self, item_line_id):
        for x in self.data:
            if x["id"] == item_line_id:
                return x
        return None

    def add_item_line(self, item_line):
        if self.is_debug:
            item_line["id"] = len(self.data) + 1
            item_line["created_at"] = self.get_timestamp()
            item_line["updated_at"] = self.get_timestamp()
            self.data.append(item_line)
        else:
            added_item_line = data_provider_v2.fetch_item_line_pool().add_item_line(
                ItemLine(**item_line)
            )
            return added_item_line.model_dump()

    def update_item_line(self, item_line_id, item_line):
        item_line["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == item_line_id:
                item_line["id"] = item_line_id
                if item_line.get("created_at") is None:
                    item_line["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = item_line
                    return item_line
                else:
                    updated_item_line = (
                        data_provider_v2.fetch_item_line_pool().update_item_line(
                            item_line_id, ItemLine(**item_line)
                        )
                    )
                    return updated_item_line.model_dump()

    def remove_item_line(self, item_line_id):
        for x in self.data:
            if x["id"] == item_line_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_item_line_pool().archive_item_line(
                        item_line_id
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = ITEM_LINES
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
