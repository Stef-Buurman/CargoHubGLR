from unittest.mock import MagicMock
import pytest
from app.models.v2.transfer import Transfer
from app.models.v2.inventory import Inventory
from app.services.v2.model_services.transfer_service import TransferService
from tests.test_globals import *

TEST_TRANSFERS = [
    Transfer(
        id=1,
        reference="TR00001",
        transfer_from=4356,
        transfer_to=9229,
        transfer_status="Completed",
        created_at="2000-03-11T13:11:14Z",
        updated_at="2000-03-12T16:11:14Z",
        items=[{"item_id": "P007435", "amount": 23}],
        is_archived=False,
    ),
    Transfer(
        id=2,
        reference="TR00002",
        transfer_from=9229,
        transfer_to=9284,
        transfer_status="Completed",
        created_at="2017-09-19T00:33:14Z",
        updated_at="2017-09-20T01:33:14Z",
        items=[{"item_id": "P007435", "amount": 23}],
        is_archived=False,
    ),
    Transfer(
        id=3,
        reference="TR00003",
        transfer_from=None,
        transfer_to=9199,
        transfer_status="Completed",
        created_at="2000-03-11T13:11:14Z",
        updated_at="2000-03-12T14:11:14Z",
        items=[{"item_id": "P009557", "amount": 1}],
        is_archived=False,
    ),
]

test_item_in_object = [
    ("p10011", 1, 1),
    ("p10012", 2, 1),
    ("p10011", 2, 2),
    ("p10012", 3, 3),
]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return MagicMock()


@pytest.fixture
def mock_get_connection(mock_db_service):
    """Fixture to mock the get_connection method with a context manager."""

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_db_service.get_connection.return_value = mock_conn

    mock_cursor = MagicMock()
    mock_conn.execute.return_value = mock_cursor

    data_provider_mock = MagicMock()

    return mock_db_service, mock_conn, mock_cursor, data_provider_mock


@pytest.fixture
def mock_pools(mock_db_service, mock_get_connection):
    """Fixture to create a mocked PoolsService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )

    item_pool_mock = MagicMock()
    data_provider_mock.fetch_item_pool.return_value = item_pool_mock

    item_pool_mock.is_item_archived.return_value = False

    inventory_pool_mock = MagicMock()
    data_provider_mock.fetch_inventory_pool.return_value = inventory_pool_mock

    inventory_pool_mock.is_inventory_archived.return_value = False

    warehouse_pool_mock = MagicMock()
    data_provider_mock.fetch_warehouse_pool.return_value = warehouse_pool_mock

    warehouse_pool_mock.is_warehouse_archived.return_value = False

    return item_pool_mock, inventory_pool_mock, warehouse_pool_mock


@pytest.fixture
def transfer_service(mock_db_service, mock_get_connection):
    """Fixture to create an TransferService instance with the mocked DatabaseService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )
    mock_db_service.get_all.return_value = TEST_TRANSFERS
    mock_cursor.fetchall.return_value = test_item_in_object
    service = TransferService(mock_db_service, data_provider_mock, True)
    return service


def test_get_all_transfers(transfer_service, mock_db_service):
    transfers = transfer_service.get_all_transfers()

    assert len(transfers) == len(transfer_service.data)
    assert transfers[0].reference == "TR00001"
    assert mock_db_service.get_all.call_count == 2


def test_get_transfers(transfer_service):
    transfers = transfer_service.get_transfers()

    assert len(transfers) == 3
    assert all(not transfer.is_archived for transfer in transfers)


def test_get_transfer(transfer_service):
    transfer = transfer_service.get_transfer(1)

    assert transfer is TEST_TRANSFERS[0]


def test_get_transfer_from_db(transfer_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    transfer_to_return = Transfer(
        id=4,
        reference="TR00004",
        transfer_from=9229,
        transfer_to=9284,
        transfer_status="Pending",
        created_at="2022-05-12T08:54:35Z",
        updated_at="2022-05-12T08:54:35Z",
        items=[{"item_id": "P007435", "amount": 23}],
        is_archived=True,
    )

    mock_cursor.description = pydantic_models_keys_to_tuple_array(transfer_to_return)

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(
        transfer_to_return
    )

    transfer = transfer_service.get_transfer(4)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 3
    assert transfer.id == transfer_to_return.id


def test_get_items_in_transfer(transfer_service):
    items = transfer_service.get_items_in_transfer(1)

    assert len(items) == 2
    assert items[0].item_id == test_item_in_object[0][0]
    assert items[0].amount == test_item_in_object[0][1]


def test_get_items_in_transfer_not_found(transfer_service):
    items = transfer_service.get_items_in_transfer(4)

    assert items == None


def test_add_transfer(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    transfer = Transfer(
        id=4,
        reference="TR00004",
        transfer_from=9229,
        transfer_to=9284,
        transfer_status="Pending",
        created_at="2022-05-12T08:54:35Z",
        updated_at="2022-05-12T08:54:35Z",
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
        is_archived=False,
    )

    result = transfer_service.add_transfer(transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 4
    assert transfer in transfer_service.data
    assert result.id == transfer.id


def test_add_transfer_has_archived_entities_item(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools

    item_pool_mock.is_item_archived.return_value = True
    new_transfer = Transfer(
        id=5,
        reference="TR00005",
        transfer_from=9229,
        transfer_to=9284,
        transfer_status="Pending",
        created_at="2022-05-12T08:54:35Z",
        updated_at="2022-05-12T08:54:35Z",
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
        is_archived=False,
    )

    result = transfer_service.add_transfer(new_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert new_transfer not in transfer_service.data


def test_add_transfer_has_archived_entities_warehouse(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools

    item_pool_mock.is_item_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = True
    new_transfer = Transfer(
        id=5,
        reference="TR00005",
        transfer_from=9229,
        transfer_to=9284,
        transfer_status="Pending",
        created_at="2022-05-12T08:54:35Z",
        updated_at="2022-05-12T08:54:35Z",
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
        is_archived=False,
    )

    result = transfer_service.add_transfer(new_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert new_transfer not in transfer_service.data


def test_update_order(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools
    warehouse_pool_mock.is_warehouse_archived.return_value = False

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    updated_transfer = transfer.copy(update={"transfer_status": "Pending"})
    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(updated_transfer)

    result = transfer_service.update_transfer(transfer_id, updated_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 5
    assert result.transfer_status == "Pending"
    updated_transfer = transfer_service.get_transfer(transfer_id)
    assert updated_transfer.transfer_status == "Pending"


def test_update_transfer_archived_item(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools
    item_pool_mock.is_item_archived.return_value = True
    warehouse_pool_mock.is_warehouse_archived.return_value = False

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    updated_transfer = transfer.copy(update={"transfer_status": "Completed"})

    result = transfer_service.update_transfer(transfer_id, updated_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_transfer_archived_warehouse_transfer_from(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools
    warehouse_pool_mock.is_warehouse_archived.return_value = True
    item_pool_mock.is_item_archived.return_value = False

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    updated_transfer = transfer.copy(update={"transfer_from": 3442})

    result = transfer_service.update_transfer(transfer_id, updated_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_transfer_archived_warehouse_transfer_to(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):

    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools
    warehouse_pool_mock.is_warehouse_archived.return_value = True
    item_pool_mock.is_item_archived.return_value = False

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    updated_transfer = transfer.copy(update={"transfer_to": 3442})

    result = transfer_service.update_transfer(transfer_id, updated_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_transfer_archived(
    transfer_service, mock_db_service, mock_get_connection
):
    transfer_id = 3
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    updated_transfer = transfer.copy(update={"transfer_status": "Shipped"})

    result = transfer_service.archive_transfer(transfer_id)
    assert result.is_archived == True
    assert mock_db_service.get_connection().__enter__().execute.call_count == 2

    result = transfer_service.update_transfer(transfer_id, updated_transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result is None
    updated_transfer = transfer_service.get_transfer(transfer_id)
    assert updated_transfer.is_archived


def test_commit_transfer(
    transfer_service, mock_db_service, mock_get_connection, mock_pools
):
    item_pool_mock, inventory_pool_mock, warehouse_pool_mock = mock_pools

    inventory_pool_mock.get_inventories_for_item.return_value = [
        Inventory(
            id=1,
            item_id="p10011",
            description="Item 10011 Description",
            item_reference="Ref10011",
            locations=[1, 4356],
            total_on_hand=50,
            total_expected=20,
            total_ordered=30,
            total_allocated=10,
            total_available=40,
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:00:00Z",
            is_archived=False,
        ),
        Inventory(
            id=2,
            item_id="p10012",
            description="Item 10012 Description",
            item_reference="Ref10012",
            locations=[9229, 4],
            total_on_hand=60,
            total_expected=25,
            total_ordered=35,
            total_allocated=15,
            total_available=45,
            created_at="2023-01-02T10:00:00Z",
            updated_at="2023-01-02T10:00:00Z",
            is_archived=False,
        ),
    ]

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    result = transfer_service.commit_transfer(transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result.transfer_status == "Processed"
    assert transfer_service.get_transfer(transfer_id).transfer_status == "Processed"


def test_archive_transfer(transfer_service, mock_db_service, mock_get_connection):
    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    result = transfer_service.archive_transfer(transfer_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.is_archived == True
    assert transfer_service.get_transfer(transfer_id).is_archived


def test_commit_archived_transfer(
    transfer_service, mock_db_service, mock_get_connection
):
    transfer_id = 3
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    result = transfer_service.commit_transfer(transfer)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert transfer_service.get_transfer(transfer_id).transfer_status == "Completed"


def test_archive_transfer_not_found(
    transfer_service, mock_db_service, mock_get_connection
):
    result = transfer_service.archive_transfer(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_is_transfer_archived(transfer_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    transfer_id = 1
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(transfer)

    result = transfer_service.is_transfer_archived(transfer_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == True


def test_is_transfer_archived_not_found(
    transfer_service, mock_db_service, mock_get_connection
):
    result = transfer_service.is_transfer_archived(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_unarchive_transfer(transfer_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    transfer_id = 3
    transfer = transfer_service.get_transfer(transfer_id)
    assert transfer is not None

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(transfer)

    result = transfer_service.unarchive_transfer(transfer_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.is_archived == False
    assert not transfer_service.get_transfer(transfer_id).is_archived


def test_unarchive_transfer_not_found(
    transfer_service, mock_db_service, mock_get_connection
):
    result = transfer_service.unarchive_transfer(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None
