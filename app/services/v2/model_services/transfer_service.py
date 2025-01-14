from services.v2.data_provider_v2 import fetch_inventory_pool
from models.v2.transfer import Transfer
from models.v2.ItemInObject import ItemInObject
from typing import List, Type
from services.v2.base_service import Base
from utils.globals import *
from services.v2.database_service import DB, DatabaseService
from services.v2 import data_provider_v2
from services.v1 import data_provider


class TransferService(Base):
    def __init__(self, db: Type[DatabaseService] = None, is_debug: bool = False):
        self.is_debug = is_debug
        if db is not None:
            self.db = db
        else:  # pragma: no cover
            self.db = DB
        self.load()

    def get_all_transfers(self) -> List[Transfer]:
        query = f"""
        SELECT t.*, ti.item_uid, ti.amount
        FROM {Transfer.table_name()} t
        LEFT JOIN {transfer_items_table} ti ON t.id = ti.transfer_id
        """
        transfers_dict = {}
        with self.db.get_connection() as conn:
            cursor = conn.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                row_dict = dict(zip(columns, row))
                transfer_id = row_dict["id"]
                if transfer_id not in transfers_dict:
                    transfers_dict[transfer_id] = Transfer(
                        **{
                            k: v
                            for k, v in row_dict.items()
                            if k not in ["item_uid", "amount"]
                        }
                    )
                    transfers_dict[transfer_id].items = []
                if row_dict["item_uid"] is not None:
                    transfers_dict[transfer_id].items.append(
                        ItemInObject(
                            item_id=row_dict["item_uid"], amount=row_dict["amount"]
                        )
                    )
        return list(transfers_dict.values())

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

        query = f"SELECT * FROM {Transfer.table_name()} WHERE id = {transfer_id}"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query)
            transfer = cursor.fetchone()
            if transfer:
                cursor_items = conn.execute(
                    f"""
                SELECT t.*, ti.item_uid, ti.amount
                FROM {Transfer.table_name()} t
                LEFT JOIN {transfer_items_table} ti ON t.id = ti.transfer_id
                WHERE t.id = {transfer_id}
                """
                )

                columns = [column[0] for column in cursor_items.description]
                rows = cursor_items.fetchall()
                transfer["items"] = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    if row_dict["item_uid"] is not None:
                        transfer["items"].append(
                            ItemInObject(
                                item_id=row_dict["item_uid"], amount=row_dict["amount"]
                            )
                        )
                return Transfer(**transfer)
        return None

    def get_items_in_transfer(self, transfer_id: int) -> List[ItemInObject]:
        for transfer in self.data:
            if transfer.id == transfer_id:
                return transfer.items
        return None

    def add_transfer(self, transfer: Transfer) -> Transfer:
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
        self.save()
        return transfer

    def update_transfer(self, transfer_id: int, transfer: Transfer) -> Transfer:
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
                self.save()
                return transfer
        return None

    def commit_transfer(self, transfer: Transfer):
        if transfer.is_archived:
            return None

        transfer_items = self.get_items_in_transfer(transfer.id)

        for item in transfer_items:
            inventories = fetch_inventory_pool().get_inventories_for_item(item.item_id)

            for y in inventories:
                if transfer.transfer_from in y.locations:
                    y.total_on_hand -= item.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    fetch_inventory_pool().update_inventory(y.id, y)
                elif transfer.transfer_to in y.locations:
                    y.total_on_hand += item.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    fetch_inventory_pool().update_inventory(y.id, y)

        transfer.transfer_status = "Processed"
        self.save()
        return transfer

    def archive_transfer(self, transfer_id: int) -> bool:
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

                self.save()
                return True
        return False

    def unarchive_transfer(self, transfer_id: int) -> bool:
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

                self.save()
                return True
        return False

    def save(self):
        if not self.is_debug:
            data_provider.fetch_transfer_pool().save(
                [transfer.model_dump() for transfer in self.data]
            )

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
                data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                    new_transfer.transfer_from
                )
                or data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                    new_transfer.transfer_to
                )
            )
            for item in new_transfer.items:
                has_archived_entities = (
                    has_archived_entities
                    or data_provider_v2.fetch_item_pool().is_item_archived(item.item_id)
                )
        else:
            if new_transfer.transfer_from != old_transfer.transfer_from:
                has_archived_entities = (
                    data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                        new_transfer.transfer_from
                    )
                )
            if new_transfer.transfer_to != old_transfer.transfer_to:
                has_archived_entities = (
                    data_provider_v2.fetch_warehouse_pool().is_warehouse_archived(
                        new_transfer.transfer_to
                    )
                )
            for item in new_transfer.items:
                has_archived_entities = (
                    has_archived_entities
                    or data_provider_v2.fetch_item_pool().is_item_archived(item.item_id)
                )
        return has_archived_entities
