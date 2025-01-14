import json
from models.v2.location import Location

from .base import Base
from services.v2 import data_provider_v2

LOCATIONS = []


class Locations(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "locations.json"
        self.load(is_debug)

    def get_locations(self):
        return self.data

    def get_location(self, location_id):
        for x in self.data:
            if x["id"] == location_id:
                return x
        return None

    def get_locations_in_warehouse(self, warehouse_id):
        result = []
        for x in self.data:
            if x["warehouse_id"] == warehouse_id:
                result.append(x)
        return result

    def add_location(self, location):
        if self.is_debug:
            location["created_at"] = self.get_timestamp()
            location["updated_at"] = self.get_timestamp()
            self.data.append(location)
            return location
        else:
            created_location = data_provider_v2.fetch_location_pool().add_location(
                Location(**location)
            )
            return created_location.model_dump()

    def update_location(self, location_id, location):
        location["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == location_id:
                location["id"] = location_id
                if location.get("created_at") is None:
                    location["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = location
                    return location
                else:
                    updated_location = (
                        data_provider_v2.fetch_location_pool().update_location(
                            location_id, Location(**location)
                        )
                    )
                    return updated_location.model_dump()

    def remove_location(self, location_id):
        for x in self.data:
            if x["id"] == location_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_location_pool().archive_location(location_id)

    def load(self, is_debug):
        if is_debug:
            self.data = LOCATIONS
        else:  
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):  
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
