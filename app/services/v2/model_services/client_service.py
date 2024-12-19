from typing import List, Type
from models.v2.client import Client
from services.v2.base_service import Base
from services.v2.database_service import DB, DatabaseService


class ClientService(Base):
    def __init__(
        self,
        db: Type[DatabaseService] = None,
    ):
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = DB
        self.load()

    def get_all_clients(self) -> List[Client]:
        return self.db.get_all(Client)

    def get_clients(self) -> List[Client]:
        clients = []
        for client in self.data:
            if not client.is_archived:
                clients.append(client)
        return clients

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
    ) -> Client | None:
        if self.is_client_archived(client_id):
            return None

        client.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                updated_client = self.db.update(client, client_id, closeConnection)
                self.data[i] = updated_client
                return updated_client
        return None

    def archive_client(
        self, client_id: int, closeConnection: bool = True
    ) -> Client | None:
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                updated_client = self.db.update(
                    self.data[i], client_id, closeConnection
                )
                self.data[i] = updated_client
                return updated_client
        return None

    def unarchive_client(
        self, client_id: int, closeConnection: bool = True
    ) -> Client | None:
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i].is_archived = False
                self.data[i].updated_at = self.get_timestamp()
                updated_client = self.db.update(
                    self.data[i], client_id, closeConnection
                )
                self.data[i] = updated_client
                return updated_client
        return None

    def is_client_archived(self, client_id: int) -> bool | None:
        for client in self.data:
            if client.id == client_id:
                return client.is_archived
        return None

    def load(self):
        self.data = self.get_all_clients()
