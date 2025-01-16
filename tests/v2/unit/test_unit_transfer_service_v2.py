from unittest.mock import MagicMock
import pytest
from app.models.v2.ItemInObject import ItemInObject
from app.models.v2.transfer import Transfer
from app.models.v2.item import Item
from app.models.v2.inventory import Inventory
from app.services.v2.model_services.transfer_service import TransferService
from tests.test_globals import *

TEST_TRANSFERS = [
    Transfer(
        id=1,
        reference="TR00001",
        transfer_from=None,
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

    return item_pool_mock, inventory_pool_mock


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
