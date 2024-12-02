from typing import List
from models.v2.item_line import ItemLine
from models.base import Base
from services.database_service import DB
from services import data_provider_v2

ITEM_LINES = []


class ItemLineService(Base):
    def __init__(self, is_debug=False):
        self.db = DB
        self.load(is_debug)

    def get_item_lines(self) -> List[ItemLine]:
        return self.db.get_all(ItemLine)

    def get_item_line(self, item_line_id: int) -> ItemLine | None:
        for item_line in self.data:
            if item_line.id == item_line_id:
                return item_line
        return self.db.get(ItemLine, item_line_id)

    def add_item_line(
        self, item_line: ItemLine, closeConnection: bool = True
    ) -> ItemLine:
        item_line.created_at = self.get_timestamp()
        item_line.updated_at = self.get_timestamp()
        self.data.append(item_line)
        return self.db.insert(item_line, closeConnection)

    def update_item_line(
        self, item_line_id: int, item_line: ItemLine, closeConnection: bool = True
    ) -> ItemLine:
        item_line.updated_at = self.get_timestamp()
        if self.get_item_line(item_line_id) is not None:
            self.data[self.data.index(self.get_item_line(item_line_id))] = item_line
        return self.db.update(item_line, item_line_id, closeConnection)

    def remove_item_line(self, item_line_id: int, closeConnection: bool = True) -> bool:
        if (
            len(
                data_provider_v2.fetch_item_pool().get_items_for_item_line(item_line_id)
            )
            > 0
        ):
            return False
        self.data.remove(self.get_item_line(item_line_id))
        return self.db.delete(ItemLine, item_line_id, closeConnection)

    def load(self, is_debug: bool, item_lines: List[ItemLine] | None = None):
        if is_debug and item_lines is not None:
            self.data = item_lines
        else:
            self.data = self.get_item_lines()
