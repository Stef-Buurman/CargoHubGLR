from typing import List, Type
from services.v2 import data_provider_v2
from models.v2.client import Client
from services.v2.base_service import Base
from services.v2.database_service import DatabaseService
from services.v1 import data_provider


class ClientService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()
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

    def add_client(self, client: Client, background_task=True) -> Client:
        client.created_at = self.get_timestamp()
        client.updated_at = self.get_timestamp()
        added_client = self.db.insert(client)
        self.data.append(added_client)
        self.save(background_task)
        return added_client

    def update_client(
        self, client_id: int, client: Client, background_task=True
    ) -> Client | None:
        if self.is_client_archived(client_id):
            return None

        client.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                client.id = client_id
                if client.created_at is None:
                    client.created_at = self.data[i].created_at
                updated_client = self.db.update(client, client_id)
                self.data[i] = updated_client
                self.save(background_task)
                return updated_client
        return None

    def archive_client(self, client_id: int, background_task=True) -> Client | None:
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i].is_archived = True
                self.data[i].updated_at = self.get_timestamp()
                updated_client = self.db.update(self.data[i], client_id)
                self.data[i] = updated_client
                self.save(background_task)
                return updated_client
        return None

    def unarchive_client(self, client_id: int, background_task=True) -> Client | None:
        for i in range(len(self.data)):
            if self.data[i].id == client_id:
                self.data[i].is_archived = False
                self.data[i].updated_at = self.get_timestamp()
                updated_client = self.db.update(self.data[i], client_id)
                self.data[i] = updated_client
                self.save(background_task)
                return updated_client
        return None

    def is_client_archived(self, client_id: int) -> bool | None:
        for client in self.data:
            if client.id == client_id:
                return client.is_archived
        return None

    def save(self, background_task=True):  # pragma: no cover:
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_client_pool().save(
                    [client.model_dump() for client in self.data]
                )

            if background_task:
                data_provider_v2.fetch_background_tasks().add_task(call_v1_save_method)
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_clients()
