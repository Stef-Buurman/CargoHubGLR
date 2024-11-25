import json
from typing import List
from models.v2.client import Client
from models.base import Base
from services.database_service import DB

CLIENTS = []


class ClientService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "clients.json"
        self.db = DB
        self.load(is_debug)

    def get_clients(self) -> List[Client]:
        return self.db.get_all(Client)

    def get_client(self, client_id: int) -> Client | None:
        for client in self.data:
            if client.id == client_id:
                return client
        return None

    def add_client(self, client: Client, closeConnection: bool = True) -> Client:
        client.created_at = self.get_timestamp()
        client.updated_at = self.get_timestamp()
        added_client = self.db.insert(client, closeConnection)
        self.data.append(added_client)
        return added_client

    def update_client(
        self, client_id: int, client: Client, closeConnection: bool = True
    ):
        client.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i] = client
                break
        return self.db.update(client, client_id, closeConnection)

    def remove_client(self, client_id: int, closeConnection: bool = True):
        for x in self.data:
            if x.id == client_id:
                if self.db.delete(Client, client_id, closeConnection):
                    self.data.remove(x)

    def load(self, is_debug: bool, clients: List[Client] | None = None):
        if is_debug and clients is not None:
            self.data = clients
        else:
            self.data = self.get_clients()
