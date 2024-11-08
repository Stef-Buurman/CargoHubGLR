import json
from services.data_provider_v2 import fetch_inventory_pool
from models.v2.transfer import Transfer
from typing import List
from models.base import Base

TRANSFERS = []


class TransferService(Base):
    def __init__(self, root_path, is_debug=False):
        self.data_path = root_path + "transfers.json"
        self.load(is_debug)

    def get_transfers(self) -> List[Transfer]:
        return self.data

    def get_transfer(self, transfer_id: int) -> Transfer | None:
        for x in self.data:
            if x.id == transfer_id:
                return x
        return None

    def get_items_in_transfer(self, transfer_id: int):
        for x in self.data:
            if x.id == transfer_id:
                return x.items
        return None

    def add_transfer(self, transfer: Transfer):
        transfer.transfer_status = "Scheduled"
        transfer.created_at = self.get_timestamp()
        transfer.updated_at = self.get_timestamp()
        self.data.append(transfer)
        return transfer

    def update_transfer(self, transfer_id: int, transfer: Transfer):
        transfer.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == transfer_id:
                self.data[i] = transfer
                break
        return transfer

    def commit_transfer(self, transfer: Transfer):
        for x in transfer.items:
            inventories = fetch_inventory_pool().get_inventories_for_item(x.item_id)

            for y in inventories:
                if transfer.transfer_from in y.locations:
                    y.total_on_hand -= x.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    fetch_inventory_pool().update_inventory(y.id, y)
                elif transfer.transfer_to in y.locations:
                    y.total_on_hand += x.amount
                    y.total_expected = y.total_on_hand + y.total_ordered
                    y.total_available = y.total_on_hand - y.total_allocated
                    fetch_inventory_pool().update_inventory(y.id, y)

        transfer.transfer_status = "Processed"
        return transfer

    def remove_transfer(self, transfer_id: int):
        for x in self.data:
            if x.id == transfer_id:
                self.data.remove(x)

    def load(self, is_debug: bool, transfers: List[Transfer] | None = None):
        if is_debug and transfers is not None:
            self.data = transfers
        else:
            with open(self.data_path, "r") as f:
                raw_data = json.load(f)
                self.data = [Transfer(**transfer_dict) for transfer_dict in raw_data]

    def save(self):
        with open(self.data_path, "w") as f:
            json.dump([transfer.model_dump() for transfer in self.data], f)
