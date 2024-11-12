import json
from typing import List
from models.v2.item_line import ItemLine
from models.base import Base
from services.database_service import DatabaseService

ITEM_LINES = []


class ItemLineService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "item_lines.json"
        self.load(is_debug)
        self.db = DatabaseService()

    def get_item_lines(self) -> List[ItemLine]:
        return self.data

    def get_item_line(self, item_line_id: int) -> ItemLine | None:
        for x in self.data:
            if x.id == item_line_id:
                return x
        return None

    def add_item_line(self, item_line: ItemLine) -> ItemLine:
        item_line.created_at = self.get_timestamp()
        item_line.updated_at = self.get_timestamp()
        self.data.append(item_line)
        return item_line

    def update_item_line(self, item_line_id: int, item_line: ItemLine) -> ItemLine:
        item_line.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_line_id:
                self.data[i] = item_line
                break
        return item_line

    def remove_item_line(self, item_line_id: int):
        for x in self.data:
            if x.id == item_line_id:
                self.data.remove(x)

    def load(self, is_debug: bool, item_lines: List[ItemLine] | None = None):
        if is_debug and item_lines is not None:
            self.data = item_lines
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [
                    ItemLine(**item_lines_dict) for item_lines_dict in raw_data
                ]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([item_line.model_dump() for item_line in self.data], f)

    def insert_item_line(self, item_line: ItemLine):
        item_line.created_at = self.get_timestamp()
        item_line.updated_at = self.get_timestamp()
        return self.db.insert(item_line)