from models.v2.location import Location
from typing import List
from services.v2.base_service import Base
from services.v2.database_service import DB


class LocationService(Base):
    def __init__(self, is_debug=False, locations: List[Location] | None = None):
        self.db = DB
        self.load(is_debug, locations)

    def get_locations(self) -> List[Location]:
        return self.db.get_all(Location)

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

    def add_location(
        self, location: Location, closeConnection: bool = True
    ) -> Location:
        location.created_at = self.get_timestamp()
        location.updated_at = self.get_timestamp()
        self.data.append(location)
        return self.db.insert(location, closeConnection)

    def update_location(
        self, location_id: int, location: Location, closeConnection: bool = True
    ) -> Location:
        location.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                self.data[i] = location
        return self.db.update(location, location_id, closeConnection)

    def remove_location(self, location_id: int, closeConnection: bool = True) -> bool:
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                if self.db.delete(Location, location_id, closeConnection):
                    del self.data[i]
                    return True
        return False

    def load(self, is_debug: bool, locations: List[Location] | None = None):
        if is_debug and locations is not None:
            self.data = locations
        else:
            self.data = self.get_locations()
