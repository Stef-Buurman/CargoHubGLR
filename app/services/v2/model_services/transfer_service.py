from models.v2.transfer import Transfer
from models.v2.ItemInObject import ItemInObject
from typing import List, Type
from services.v2.base_service import Base
from utils.globals import *
from services.v2.database_service import DatabaseService
from services.v2 import data_provider_v2
from services.v1 import data_provider


class TransferService(Base):
    def __init__(
        self,
        db: Type[DatabaseService] = None,
        data_provider=None,
        is_debug: bool = False,
    ):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:
            self.db = data_provider_v2.fetch_database()

        if data_provider is not None:
            self.data_provider = data_provider
        else:
            self.data_provider = data_provider_v2

        self.load()

    def get_all_transfers(self) -> List[Transfer]:
        all_transfers = self.db.get_all(Transfer)
        transfer_ids = [transfer.id for transfer in all_transfers]
        with self.db.get_connection() as conn:
            query = f"SELECT item_uid, amount, transfer_id FROM {transfer_items_table} WHERE transfer_id IN ({', '.join(map(str, transfer_ids))})"
            cursor = conn.execute(query)
            all_transfer_items = cursor.fetchall()
        transfer_items_map = {}
        for row in all_transfer_items:
            if row[2] not in transfer_items_map:
                transfer_items_map[row[2]] = []
            transfer_items_map[row[2]].append(
                ItemInObject(item_id=row[0], amount=row[1])
            )
        for transfer in all_transfers:
            transfer.items = transfer_items_map.get(transfer.id, [])
        return all_transfers

    def get_transfers(self) -> List[Transfer]:
        transfers = []
        for transfer in self.data:
            if not transfer.is_archived:
                transfers.append(transfer)
        return transfers

    def get_transfer(self, transfer_id: int) -> Transfer | None:
        for transfer in self.data:
            if transfer.id == transfer_id:
                return transfer
        with self.db.get_connection() as conn:
            query = f"SELECT * FROM {Transfer.table_name()} WHERE id = ?"
            cursor = conn.execute(query, (transfer_id,))
            transfer_row = cursor.fetchone()
            if transfer_row:
                column_names = [description[0] for description in cursor.description]
                transfer = dict(zip(column_names, transfer_row))
                query_items = f"SELECT item_uid, amount, transfer_id FROM {transfer_items_table} WHERE transfer_id = ?"
                cursor = conn.execute(query_items, (transfer_id,))
                all_transfer_items = cursor.fetchall()
                transfer["items"] = [
                    ItemInObject(item_id=row[0], amount=row[1])
                    for row in all_transfer_items
                ]
                return Transfer(**transfer)
        return None

    def get_items_in_transfer(self, transfer_id: int) -> List[ItemInObject]:
        for transfer in self.data:
            if transfer.id == transfer_id:
                return transfer.items
        return None

    def add_transfer(self, transfer: Transfer, background_task=True) -> Transfer:
        if self.has_transfer_archived_entities(transfer):
            return None

        table_name = transfer.table_name()

        transfer.created_at = self.get_timestamp()
        transfer.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(transfer).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        values = tuple(fields.values())

        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with self.db.get_connection() as conn:
            cursor = conn.execute(insert_sql, values)
            transfer_id = cursor.lastrowid
            transfer.id = transfer_id

            if transfer.items:
                for transfer_items in transfer.items:
                    items_insert_sql = f"""
                    INSERT INTO {transfer_items_table} (transfer_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (transfer_id, transfer_items.item_id, transfer_items.amount),
                    )

        self.data.append(transfer)
        self.save(background_task)
        return transfer

    def update_transfer(
        self, transfer_id: int, transfer: Transfer, background_task=True
    ) -> Transfer:
        old_transfer = self.get_transfer(transfer_id)
        if self.is_transfer_archived(
            transfer_id
        ) is not False or self.has_transfer_archived_entities(transfer, old_transfer):
            return None

        table_name = transfer.table_name()

        transfer.updated_at = self.get_timestamp()

        fields = {}
        for key, value in vars(transfer).items():
            if key != "id" and key != "items":
                fields[key] = value

        columns = ", ".join(f"{key} = ?" for key in fields)
        values = tuple(fields.values())

        update_sql = f"UPDATE {table_name} SET {columns} WHERE id = ?"
        values += (transfer_id,)

        with self.db.get_connection() as conn:
            conn.execute(update_sql, values)

            if transfer.items:
                conn.execute(
                    f"DELETE FROM {transfer_items_table} WHERE transfer_id = ?",
                    (transfer_id,),
                )

                for transfer_items in transfer.items:
                    items_insert_sql = f"""
                    INSERT INTO {transfer_items_table} (transfer_id, item_uid, amount)
                    VALUES (?, ?, ?)
                    """
                    conn.execute(
                        items_insert_sql,
                        (transfer_id, transfer_items.item_id, transfer_items.amount),
                    )

        for i in range(len(self.data)):
            if self.data[i].id == transfer_id:
                transfer.id = transfer_id
                if transfer.created_at is None:
                    transfer.created_at = self.data[i].created_at
                self.data[i] = transfer
                self.save(background_task)
                return transfer
        return None

    def commit_transfer(self, transfer: Transfer, background_task=True):
        if transfer.is_archived:
            return None

        transfer_items = self.get_items_in_transfer(transfer.id)

        for item in transfer_items:
            inventories = (
                self.data_provider.fetch_inventory_pool().get_inventories_for_item(
                    item.item_id
                )
            )

            for y in inventories:
                if transfer.transfer_from in y.locations:
                    y.total_on_hand -= item.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    self.data_provider.fetch_inventory_pool().update_inventory(y.id, y)
                elif transfer.transfer_to in y.locations:
                    y.total_on_hand += item.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    self.data_provider.fetch_inventory_pool().update_inventory(y.id, y)

        transfer.transfer_status = "Processed"
        self.save(background_task)
        return transfer

    def archive_transfer(self, transfer_id: int, background_task=True) -> bool:
        for i in range(len(self.data)):
            if self.data[i].id == transfer_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = True

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = (
                    f"UPDATE {self.data[i].table_name()} SET {columns} WHERE id = ?"
                )
                values += (transfer_id,)

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values)

                self.save(background_task)
                return self.data[i]
        return None

    def unarchive_transfer(self, transfer_id: int, background_task=True) -> bool:
        for i in range(len(self.data)):
            if self.data[i].id == transfer_id:
                self.data[i].updated_at = self.get_timestamp()
                self.data[i].is_archived = False

                fields = {}
                for key, value in vars(self.data[i]).items():
                    if key != "id" and key != "items":
                        fields[key] = value

                columns = ", ".join(f"{key} = ?" for key in fields)
                values = tuple(fields.values())

                update_sql = (
                    f"UPDATE {self.data[i].table_name()} SET {columns} WHERE id = ?"
                )
                values += (transfer_id,)

                with self.db.get_connection() as conn:
                    conn.execute(update_sql, values)

                self.save(background_task)
                return self.data[i]
        return None

    def save(self, background_task=True):
        if not self.is_debug:

            def call_v1_save_method():
                data_provider.fetch_transfer_pool().save(
                    [shipment.model_dump() for shipment in self.data]
                )

            if background_task:
                self.data_provider.fetch_background_tasks().add_task(
                    call_v1_save_method
                )
            else:
                call_v1_save_method()

    def load(self):
        self.data = self.get_all_transfers()

    def is_transfer_archived(self, transfer_id: int) -> bool:
        for transfer in self.data:
            if transfer.id == transfer_id:
                return transfer.is_archived
        return None

    def has_transfer_archived_entities(
        self, new_transfer: Transfer, old_transfer: Transfer | None = None
    ) -> bool:
        has_archived_entities = False

        if old_transfer is None:
            has_archived_entities = (
                self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                    new_transfer.transfer_from
                )
                or self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                    new_transfer.transfer_to
                )
            )
            for item in new_transfer.items:
                has_archived_entities = (
                    has_archived_entities
                    or self.data_provider.fetch_item_pool().is_item_archived(
                        item.item_id
                    )
                )
        else:
            if new_transfer.transfer_from != old_transfer.transfer_from:
                has_archived_entities = (
                    self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                        new_transfer.transfer_from
                    )
                )
            if new_transfer.transfer_to != old_transfer.transfer_to:
                has_archived_entities = (
                    self.data_provider.fetch_warehouse_pool().is_warehouse_archived(
                        new_transfer.transfer_to
                    )
                )
            for item in new_transfer.items:
                has_archived_entities = (
                    has_archived_entities
                    or self.data_provider.fetch_item_pool().is_item_archived(
                        item.item_id
                    )
                )
        return has_archived_entities
