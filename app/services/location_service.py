from models.v2.location import Location
from typing import List
from models.base import Base
from services.database_service import DB

LOCATIONS = []


class LocationService(Base):
    def __init__(self, is_debug=False):
        self.db = DB
        self.load(is_debug)

    def get_locations(self) -> List[Location]:
        return self.db.get_all(Location)

    def get_location(self, location_id: int) -> Location | None:
        return self.db.get(Location, location_id)

    def get_locations_in_warehouse(self, warehouse_id: int):
        return [
            location
            for location in self.db.get_all(Location)
            if location.warehouse_id == warehouse_id
        ]

    def add_location(
        self, location: Location, closeConnection: bool = True
    ) -> Location:
        location.created_at = self.get_timestamp()
        location.updated_at = self.get_timestamp()
        return self.db.insert(location, closeConnection)

    def update_location(
        self, location_id: int, location: Location, closeConnection: bool = True
    ) -> Location:
        location.updated_at = self.get_timestamp()
        return self.db.update(location, location_id, closeConnection)

    def remove_location(self, location_id: int, closeConnection: bool = True) -> bool:
        return self.db.delete(Location, location_id, closeConnection)

    def load(self, is_debug: bool, locations: List[Location] | None = None):
        if is_debug and locations is not None:
            self.data = locations
        else:
            self.data = self.db.get_all(Location)
