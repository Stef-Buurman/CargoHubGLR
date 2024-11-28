from services.data_provider_v2 import fetch_inventory_pool
from models.v2.transfer import Transfer
from models.v2.ItemInObject import ItemInObject
from typing import List
from models.base import Base
from utils.globals import *
from services.database_service import DB


class TransferService(Base):
    def __init__(self, is_debug: bool = False, transfers: List[Transfer] | None = None):
        self.db = DB
        self.load(is_debug, transfers)

    def get_transfers(self) -> List[Transfer]:
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

    def get_transfer(self, transfer_id: int) -> Transfer | None:
        for transfer in self.data:
            if transfer.id == transfer_id:
                return transfer
        query = "SELECT * FROM {Transfer.table_name()} WHERE id = {transfer_id}"
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

    def add_transfer(
        self, transfer: Transfer, closeConnection: bool = True
    ) -> Transfer:
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

        with self.db.get_connection_without_close() as conn:
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

        if closeConnection:
            self.db.commit_and_close()
        return transfer

    def update_transfer(
        self, transfer_id: int, transfer: Transfer, closeConnection: bool = True
    ) -> Transfer:
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

        with self.db.get_connection_without_close() as conn:
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

        if closeConnection:
            self.db.commit_and_close()
        return transfer

    def commit_transfer(self, transfer: Transfer):
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
        return transfer

    def remove_transfer(self, transfer_id: int, closeConnection: bool = True):
        return self.db.delete(Transfer, transfer_id, closeConnection)

    def load(self, is_debug: bool, transfers: List[Transfer] | None = None):
        if is_debug and transfers is not None:
            self.data = transfers
        else:
            self.data = self.get_transfers()
