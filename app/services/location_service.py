import json
from models.v2.location import Location
from typing import List
from models.base import Base
from services.database_service import DB

LOCATIONS = []


class LocationService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "locations.json"
        self.load(is_debug)
        self.db = DB

    def get_locations(self) -> List[Location]:
        return self.data

    def get_location(self, location_id: int) -> Location | None:
        for x in self.data:
            if x.id == location_id:
                return x
        return None

    def get_locations_in_warehouse(self, warehouse_id: int):
        result = []
        for x in self.data:
            if x.warehouse_id == warehouse_id:
                result.append(x)
        return result

    def add_location(self, location: Location):
        location.created_at = self.get_timestamp()
        location.updated_at = self.get_timestamp()
        self.data.append(location)
        return location

    def update_location(self, location_id: int, location: Location):
        location.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == location_id:
                self.data[i] = location
                break
        return location

    def remove_location(self, location_id: int):
        for x in self.data:
            if x.id == location_id:
                self.data.remove(x)

    def load(self, is_debug: bool, locations: List[Location] | None = None):
        if is_debug and locations is not None:
            self.data = locations
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Location(**location_dict) for location_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([location.model_dump() for location in self.data], f)

    def insert_location(
        self, location: Location, closeConnection: bool = True
    ) -> Location:
        location.created_at = self.get_timestamp()
        location.updated_at = self.get_timestamp()
        return self.db.insert(location, closeConnection)
