import json
from typing import List
from models.v2.client import Client
from models.base import Base
from services.database_service import DB

CLIENTS = []


class ClientService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "clients.json"
        self.load(is_debug)
        self.db = DB

    def get_clients(self) -> List[Client]:
        return self.data

    def get_client(self, client_id: int) -> Client | None:
        for x in self.data:
            if x.id == client_id:
                return x
        return None

    def add_client(self, client: Client):
        client.created_at = self.get_timestamp()
        client.updated_at = self.get_timestamp()
        self.data.append(client)
        return client

    def update_client(self, client_id: int, client: Client):
        client.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i] = client
                break
        return client

    def remove_client(self, client_id: int):
        for x in self.data:
            if x.id == client_id:
                self.data.remove(x)

    def load(self, is_debug: bool, clients: List[Client] | None = None):
        if is_debug and clients is not None:
            self.data = clients
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Client(**client_dict) for client_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([client.model_dump() for client in self.data], f)

    def insert_client(self, client: Client, closeConnection: bool = True) -> Client:
        client.created_at = self.get_timestamp()
        client.updated_at = self.get_timestamp()
        return self.db.insert(client, closeConnection)
