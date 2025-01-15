import json
from models.v2.transfer import Transfer

from .base import Base
from services.v2 import data_provider_v2

TRANSFERS = []


class Transfers(Base):
    def __init__(self, root_path, is_debug=False):
        self.is_debug = is_debug
        self.data_path = root_path + "transfers.json"
        self.load(is_debug)

    def get_transfers(self):
        return self.data

    def get_transfer(self, transfer_id):
        for x in self.data:
            if x["id"] == transfer_id:
                return x
        return None

    def get_items_in_transfer(self, transfer_id):
        for x in self.data:
            if x["id"] == transfer_id:
                return x["items"]
        return None

    def add_transfer(self, transfer):
        if self.is_debug:
            transfer["transfer_status"] = "Scheduled"
            transfer["created_at"] = self.get_timestamp()
            transfer["updated_at"] = self.get_timestamp()
            self.data.append(transfer)
            return transfer
        else:
            created_transfer = data_provider_v2.fetch_transfer_pool().add_transfer(
                Transfer(**transfer), False
            )
            return created_transfer.model_dump()

    def update_transfer(self, transfer_id, transfer):
        transfer["updated_at"] = self.get_timestamp()
        for i in range(len(self.data)):
            if self.data[i]["id"] == transfer_id:
                transfer["id"] = transfer_id
                if transfer.get("created_at") is None:
                    transfer["created_at"] = self.data[i]["created_at"]
                if self.is_debug:
                    self.data[i] = transfer
                    return transfer
                else:
                    updated_transfer = (
                        data_provider_v2.fetch_transfer_pool().update_transfer(
                            transfer_id, Transfer(**transfer), False
                        )
                    )
                    return updated_transfer.model_dump()

    def remove_transfer(self, transfer_id):
        for x in self.data:
            if x["id"] == transfer_id:
                self.data.remove(x)
                if not self.is_debug:
                    data_provider_v2.fetch_transfer_pool().archive_transfer(
                        transfer_id, False
                    )

    def load(self, is_debug):
        if is_debug:
            self.data = TRANSFERS
        else:
            f = open(self.data_path, "r")
            self.data = json.load(f)
            f.close()

    def save(self, data=None):
        if data:
            self.data = data
        f = open(self.data_path, "w")
        json.dump(self.data, f)
        f.close()
