from services.v2 import data_provider_v2
from models.v2.location import Location
from typing import List, Type
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class LocationService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()
        self.load()

    def get_all_locations(self) -> List[Location]:
        return self.db.get_all(Location)

    def get_locations(self) -> List[Location]:
        locations = []
        for location in self.data:
            if not location.is_archived:
                locations.append(location)
        return locations

    def get_location(self, location_id: int) -> Location | None:
        for location in self.data:
            if location.id == location_id:
                return location
        return self.db.get(Location, location_id)

    def get_locations_in_warehouse(self, warehouse_id: int) -> List[Location]:
        warehouse_locations = []
        for location in self.data:
            if location.warehouse_id == warehouse_id:
                warehouse_locations.append(location)
        return warehouse_locations

    def add_location(self, location: Location, background_task=True) -> Location:
        if self.has_location_archived_entities(location):
            return None
        location.created_at = self.get_timestamp()
        location.updated_at = self.get_timestamp()
        added_location = self.db.insert(location)
        self.data.append(added_location)
        self.save(background_task)
        return added_location

    def update_location(
        self, location_id: int, location: Location, background_task=True
    ) -> Location | None:
        if self.is_location_archived(
            location_id
        ) or self.has_location_archived_entities(
            location, self.get_location(location_id)
        ):
            return None

        location.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                location.id = location_id
                if location.created_at is None:
                    location.created_at = self.data[i].created_at
                updated_location = self.db.update(location, location_id)
                self.data[i] = updated_location
                self.save(background_task)
                return updated_location
        return None

    def archive_location(
        self, location_id: int, background_task=True
    ) -> Location | None:
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True
                updated_location = self.db.update(self.data[i], location_id)
                self.data[i] = updated_location
                self.save(background_task)
                return updated_location
        return None

    def unarchive_location(
        self, location_id: int, background_task=True
    ) -> Location | None:
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False
                updated_location = self.db.update(self.data[i], location_id)
                self.data[i] = updated_location
                self.save(background_task)
                return updated_location
        return None

    def save(self, background_task=True): # pragma: no cover:
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_location_pool().save(
                    [item.model_dump() for item in self.data]
                )

            if background_task:
                data_provider_v2.fetch_background_tasks().add_task(call_v1_save_method)
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_locations()

    def is_location_archived(self, location_id: int) -> bool | None:
        for location in self.data:
            if location.id == location_id:
                return location.is_archived
        return None

    def has_location_archived_entities(
        self, new_location: Location, old_location: Location | None = None
    ) -> bool:
        has_archived_entities = False

        if old_location is None:
            has_archived_entities = (
                data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                    new_location.warehouse_id
                )
            )
        else:
            if new_location.warehouse_id != old_location.warehouse_id:
                has_archived_entities = (
                    data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                        new_location.warehouse_id
                    )
                )
        return has_archived_entities
