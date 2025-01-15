from typing import List, Type
from services.v2 import data_provider_v2
from models.v2.item_line import ItemLine
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class ItemLineService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = data_provider_v2.fetch_database()
        self.load()

    def get_all_item_lines(self) -> List[ItemLine]:
        return self.db.get_all(ItemLine)

    def get_item_lines(self) -> List[ItemLine]:
        item_lines = []
        for item_line in self.data:
            if not item_line.is_archived:
                item_lines.append(item_line)
        return item_lines

    def get_item_line(self, item_line_id: int) -> ItemLine | None:
        for item_line in self.data:
            if item_line.id == item_line_id:
                return item_line
        return self.db.get(ItemLine, item_line_id)

    def is_item_line_archived(self, item_line_id: int) -> bool:
        for item_line in self.data:
            if item_line.id == item_line_id:
                return item_line.is_archived
        return None

    def add_item_line(self, item_line: ItemLine, background_task=True) -> ItemLine:
        item_line.created_at = self.get_timestamp()
        item_line.updated_at = self.get_timestamp()
        added_item_line = self.db.insert(item_line)
        self.data.append(added_item_line)
        self.save(background_task)
        return added_item_line

    def update_item_line(self, item_line_id: int, item_line: ItemLine, background_task=True) -> ItemLine:
        if self.is_item_line_archived(item_line_id):
            return None

        item_line.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == item_line_id:
                updated_item_line = self.db.update(item_line, item_line_id)
                self.data[i] = updated_item_line
                self.save(background_task)
                return updated_item_line
        return None  # pragma: no cover

    def archive_item_line(self, item_line_id: int, background_task=True) -> ItemLine | None:
        for i in range(len(self.data)):
            if self.data[i].id == item_line_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                updated_item_line = self.db.update(self.data[i], item_line_id)
                self.data[i] = updated_item_line
                self.save(background_task)
                return updated_item_line
        return None

    def unarchive_item_line(self, item_line_id: int, background_task=True) -> ItemLine | None:
        for i in range(len(self.data)):
            if self.data[i].id == item_line_id:
                self.data[i].is_archived = False
                self.data[i].updated_at = self.get_timestamp()
                updated_item_line = self.db.update(self.data[i], item_line_id)
                self.data[i] = updated_item_line
                self.save(background_task)
                return updated_item_line
        return None

    def save(self, background_task=True):
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_item_line_pool().save(
                    [item.model_dump() for item in self.data]
                )

            if background_task:
                data_provider_v2.fetch_background_tasks().add_task(call_v1_save_method)
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_item_lines()
