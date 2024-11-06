import json
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

    def update_transfer(self, transfer_id: int, transfer: Transfer):
        transfer.updated_at = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i].id == transfer_id:
                self.data[i] = transfer
                break

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
