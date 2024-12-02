from typing import List
from models.v2.client import Client
from services.v2.base_service import Base
from services.v2.database_service import DB


class ClientService(Base):
    def __init__(self, is_debug=False, clients: List[Client] | None = None):
        self.db = DB
        self.load(is_debug, clients)

    def get_clients(self) -> List[Client]:
        return self.db.get_all(Client)

    def get_client(self, client_id: int) -> Client | None:
        for client in self.data:
            if client.id == client_id:
                return client
        return self.db.get(Client, client_id)

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
        for client in self.data:
            if client.id == client_id:
                if self.db.delete(Client, client_id, closeConnection):
                    self.data.remove(client)

    def load(self, is_debug: bool, clients: List[Client] | None = None):
        if is_debug and clients is not None:
            self.data = clients
        else:
            self.data = self.get_clients()
