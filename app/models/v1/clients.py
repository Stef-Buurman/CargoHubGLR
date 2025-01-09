import json
from models.v2.client import Client

from .base import Base
from services.v2 import data_provider_v2

CLIENTS = []


class Clients(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "clients.json"
        self.load(is_debug)

    def get_clients(self):
        return self.data

    def get_client(self, client_id):
        for x in self.data:
            if x["id"] == client_id:
                return x
        return None

    def add_client(self, client):
        if self.is_debug:
            client["created_at"] = self.get_timestamp()
            client["updated_at"] = self.get_timestamp()
            self.data.append(client)
            return client
        else:
            created_client = data_provider_v2.fetch_client_pool().add_client(
                Client(**client)
            )
            return created_client.model_dump()

    def update_client(self, client_id, client):
        client["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == client_id:
                client["id"] = client_id
                if client.get("created_at") is None:
                    client["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = client
                    return client
                else:
                    updated_client = data_provider_v2.fetch_client_pool().update_client(
                        client_id, Client(**client)
                    )
                    return updated_client.model_dump()

    def remove_client(self, client_id):
        for x in self.data:
            if x["id"] == client_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_client_pool().archive_client(client_id)

    def load(self, is_debug):
        if is_debug:
            self.data = CLIENTS
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
