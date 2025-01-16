from unittest.mock import MagicMock
import pytest
from app.models.v2.ItemInObject import ItemInObject
from app.models.v2.shipment import Shipment
from app.models.v2.inventory import Inventory
from app.services.v2.model_services.shipment_service import ShipmentService
from tests.test_globals import *


TEST_SHIPMENTS = [
    Shipment(
        id=1,
        order_id=101,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="Pending",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        created_at="2023-01-01T10:00:00Z",
        updated_at="2023-01-01T10:00:00Z",
        is_archived=False,
    ),
    Shipment(
        id=2,
        order_id=102,
        source_id=202,
        order_date="2023-02-01",
        request_date="2023-02-02",
        shipment_date="2023-02-03",
        shipment_type="TypeB",
        shipment_status="StatusB",
        notes="NoteB",
        carrier_code="CarrierB",
        carrier_description="Carrier Description B",
        service_code="ServiceB",
        payment_type="Collect",
        transfer_mode="Sea",
        total_package_count=20,
        total_package_weight=200.5,
        created_at="2023-02-01T10:00:00Z",
        updated_at="2023-02-01T10:00:00Z",
        is_archived=False,
    ),
    Shipment(
        id=3,
        order_id=102,
        source_id=203,
        order_date="2023-03-01",
        request_date="2023-03-02",
        shipment_date="2023-03-03",
        shipment_type="TypeC",
        shipment_status="StatusC",
        notes="NoteC",
        carrier_code="CarrierC",
        carrier_description="Carrier Description C",
        service_code="ServiceC",
        payment_type="Prepaid",
        transfer_mode="Land",
        total_package_count=30,
        total_package_weight=300.5,
        created_at="2023-03-01T10:00:00Z",
        updated_at="2023-03-01T10:00:00Z",
        is_archived=True,
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
    data_provider_mock.fetch_database.return_value = mock_db_service

    return mock_db_service, mock_conn, mock_cursor, data_provider_mock


@pytest.fixture
def mock_pools(mock_db_service, mock_get_connection):
    """Fixture to create a mocked PoolsService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )

    order_pool_mock = MagicMock()
    data_provider_mock.fetch_order_pool.return_value = order_pool_mock

    order_pool_mock.is_order_archived.return_value = False

    inventory_pool_mock = MagicMock()
    data_provider_mock.fetch_inventory_pool.return_value = inventory_pool_mock

    item_pool_mock = MagicMock()
    data_provider_mock.fetch_item_pool.return_value = item_pool_mock

    item_pool_mock.is_item_archived.return_value = False

    return order_pool_mock, inventory_pool_mock, item_pool_mock


@pytest.fixture
def shipment_service(mock_db_service, mock_get_connection):
    """Fixture to create an OrderService instance with the mocked DatabaseService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )
    mock_db_service.get_all.return_value = TEST_SHIPMENTS
    mock_cursor.fetchall.return_value = test_item_in_object
    service = ShipmentService(data_provider_mock, True)
    return service


def test_get_all_shipments(shipment_service):
    shipments = shipment_service.get_all_shipments()
    assert shipments == TEST_SHIPMENTS
    assert len(shipments) == 3
    assert shipments[0].id == 1
    assert shipments[1].id == 2
    assert shipments[2].id == 3


def test_get_shipments(shipment_service):
    shipments = shipment_service.get_shipments()
    assert shipments == TEST_SHIPMENTS[:2]
    assert len(shipments) == 2
    assert shipments[0].id == 1
    assert shipments[1].id == 2


def test_get_shipment(shipment_service):
    shipment = shipment_service.get_shipment(1)
    assert shipment == TEST_SHIPMENTS[0]
    assert shipment.id == 1


def test_get_shipment_from_db(shipment_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    shipment_to_return = Shipment(
        id=4,
        order_id=101,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="StatusA",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        created_at="2023-01-01T10:00:00Z",
        updated_at="2023-01-01T10:00:00Z",
        is_archived=False,
        items=None,
    )

    mock_cursor.description = pydantic_models_keys_to_tuple_array(shipment_to_return)

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(
        shipment_to_return
    )

    shipment = shipment_service.get_shipment(shipment_to_return.id)

    mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert shipment.id == shipment.id


def test_get_items_in_shipment(shipment_service):
    items = shipment_service.get_items_in_shipment(1)

    assert len(items) == 2
    assert items[0].item_id == test_item_in_object[0][0]
    assert items[1].item_id == test_item_in_object[1][0]


def test_add_shipment(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    new_shipment = Shipment(
        id=4,
        order_id=104,
        source_id=204,
        order_date="2024-01-01",
        request_date="2024-01-02",
        shipment_date="2024-01-03",
        shipment_type="TypeD",
        shipment_status="StatusD",
        notes="NoteD",
        carrier_code="CarrierD",
        carrier_description="Carrier Description D",
        service_code="ServiceD",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=40,
        total_package_weight=400.5,
        created_at="2024-01-01T10:00:00Z",
        updated_at="2024-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
    )

    result = shipment_service.add_shipment(new_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 4
    assert new_shipment in shipment_service.data
    assert result.source_id == new_shipment.source_id


def test_add_archived_shipment(shipment_service, mock_db_service, mock_pools):
    new_shipment = Shipment(
        id=4,
        order_id=104,
        source_id=204,
        order_date="2024-01-01",
        request_date="2024-01-02",
        shipment_date="2024-01-03",
        shipment_type="TypeD",
        shipment_status="StatusD",
        notes="NoteD",
        carrier_code="CarrierD",
        carrier_description="Carrier Description D",
        service_code="ServiceD",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=40,
        total_package_weight=400.5,
        created_at="2024-01-01T10:00:00Z",
        updated_at="2024-01-01T10:00:00Z",
        is_archived=True,
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
    )

    result = shipment_service.add_shipment(new_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_add_shipment_with_archived_order(
    shipment_service, mock_db_service, mock_pools
):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = True
    item_pool_mock.is_item_archived.return_value = False

    new_shipment = Shipment(
        id=4,
        order_id=104,
        source_id=204,
        order_date="2024-01-01",
        request_date="2024-01-02",
        shipment_date="2024-01-03",
        shipment_type="TypeD",
        shipment_status="StatusD",
        notes="NoteD",
        carrier_code="CarrierD",
        carrier_description="Carrier Description D",
        service_code="ServiceD",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=40,
        total_package_weight=400.5,
        created_at="2024-01-01T10:00:00Z",
        updated_at="2024-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
    )

    result = shipment_service.add_shipment(new_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_add_shipment_with_archived_items(
    shipment_service, mock_db_service, mock_pools
):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = True

    new_shipment = Shipment(
        id=4,
        order_id=104,
        source_id=204,
        order_date="2024-01-01",
        request_date="2024-01-02",
        shipment_date="2024-01-03",
        shipment_type="TypeD",
        shipment_status="StatusD",
        notes="NoteD",
        carrier_code="CarrierD",
        carrier_description="Carrier Description D",
        service_code="ServiceD",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=40,
        total_package_weight=400.5,
        created_at="2024-01-01T10:00:00Z",
        updated_at="2024-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 1},
            {"item_id": "p10012", "amount": 2},
        ],
    )

    result = shipment_service.add_shipment(new_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_shipment(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    updated_shipment = Shipment(
        id=1,
        order_id=101,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="Pending",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        updated_at="2023-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 2},
            {"item_id": "p10015", "amount": 3},
        ],
    )

    result = shipment_service.update_shipment(updated_shipment.id, updated_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 4
    assert updated_shipment in shipment_service.data
    assert result.source_id == updated_shipment.source_id


def test_update_shipment_with_archived_order(
    shipment_service, mock_db_service, mock_pools
):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = True
    item_pool_mock.is_item_archived.return_value = False

    updated_shipment = Shipment(
        id=1,
        order_id=105,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="Pending",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        updated_at="2023-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 2},
            {"item_id": "p10015", "amount": 3},
        ],
    )

    result = shipment_service.update_shipment(updated_shipment.id, updated_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_shipment_where_new_shipment_id_archived(
    shipment_service, mock_db_service, mock_pools
):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    updated_shipment = Shipment(
        id=1,
        order_id=101,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="Pending",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        updated_at="2023-01-01T10:00:00Z",
        is_archived=True,
        items=[
            {"item_id": "p10011", "amount": 2},
            {"item_id": "p10015", "amount": 3},
        ],
    )

    result = shipment_service.update_shipment(1, updated_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_items_in_shipment(shipment_service, mock_db_service, mock_pools):
    shipment_id = 1
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    inventory_pool_mock.get_inventories_for_item.return_value = [
        Inventory(
            id=1,
            item_id="p10011",
            description="Item 10011 Description",
            item_reference="Ref10011",
            locations=[1, 2],
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
            item_id="p10015",
            description="Item 10015 Description",
            item_reference="Ref10015",
            locations=[3, 4],
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

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    updated_items = [
        ItemInObject(item_id="p10011", amount=2),
        ItemInObject(item_id="p10015", amount=3),
    ]

    result = shipment_service.update_items_in_shipment(shipment_id, updated_items)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 4
    assert result.source_id == TEST_SHIPMENTS[0].source_id
    assert result.items == updated_items


def test_update_items_in_shipment_with_archived_items(
    shipment_service, mock_db_service, mock_pools
):
    shipment_id = 1
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    inventory_pool_mock.get_inventories_for_item.return_value = [
        Inventory(
            id=1,
            item_id="p10011",
            description="Item 10011 Description",
            item_reference="Ref10011",
            locations=[1, 2],
            total_on_hand=50,
            total_expected=20,
            total_ordered=30,
            total_allocated=10,
            total_available=40,
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:00:00Z",
            is_archived=True,
        ),
        Inventory(
            id=2,
            item_id="p10015",
            description="Item 10015 Description",
            item_reference="Ref10015",
            locations=[3, 4],
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

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = True

    updated_items = [
        ItemInObject(item_id="p10011", amount=2),
        ItemInObject(item_id="p10015", amount=3),
    ]

    result = shipment_service.update_items_in_shipment(shipment_id, updated_items)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_archive_shipment(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.archive_shipment(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.source_id == TEST_SHIPMENTS[0].source_id
    assert result.is_archived


def test_archive_shipment_not_found(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.archive_shipment(4)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_archived_shipment(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = True
    item_pool_mock.is_item_archived.return_value = False

    updated_shipment = Shipment(
        id=1,
        order_id=101,
        source_id=201,
        order_date="2023-01-01",
        request_date="2023-01-02",
        shipment_date="2023-01-03",
        shipment_type="TypeA",
        shipment_status="StatusA",
        notes="NoteA",
        carrier_code="CarrierA",
        carrier_description="Carrier Description A",
        service_code="ServiceA",
        payment_type="Prepaid",
        transfer_mode="Air",
        total_package_count=10,
        total_package_weight=100.5,
        updated_at="2023-01-01T10:00:00Z",
        is_archived=False,
        items=[
            {"item_id": "p10011", "amount": 2},
            {"item_id": "p10015", "amount": 3},
        ],
    )

    result = shipment_service.update_shipment(updated_shipment.id, updated_shipment)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_shipment_items_archived(shipment_service, mock_db_service, mock_pools):
    shipment_id = 1
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    inventory_pool_mock.get_inventories_for_item.return_value = [
        Inventory(
            id=1,
            item_id="p10011",
            description="Item 10011 Description",
            item_reference="Ref10011",
            locations=[1, 2],
            total_on_hand=50,
            total_expected=20,
            total_ordered=30,
            total_allocated=10,
            total_available=40,
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:00:00Z",
            is_archived=True,
        ),
        Inventory(
            id=2,
            item_id="p10015",
            description="Item 10015 Description",
            item_reference="Ref10015",
            locations=[3, 4],
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

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    updated_items = [
        ItemInObject(item_id="p10011", amount=2),
        ItemInObject(item_id="p10015", amount=3),
    ]

    result = shipment_service.update_items_in_shipment(shipment_id, updated_items)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_is_shipment_archived(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.is_shipment_archived(3)

    assert result


def test_is_shipment_archived_not_found(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.is_shipment_archived(4)

    assert not result


def test_unarchive_shipment(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.unarchive_shipment(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.source_id == TEST_SHIPMENTS[0].source_id
    assert not result.is_archived


def test_unarchive_shipment_not_found(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    order_pool_mock.is_order_archived.return_value = False
    item_pool_mock.is_item_archived.return_value = False

    result = shipment_service.unarchive_shipment(4)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_get_shipments_for_order(shipment_service, mock_db_service, mock_pools):
    order_pool_mock, inventory_pool_mock, item_pool_mock = mock_pools

    shipments = shipment_service.get_shipments_for_order(102)

    assert len(shipments) == 2
    assert shipments[0].id == 2
    assert shipments[0].order_id == 102
    assert shipments[1].id == 3
    assert shipments[1].order_id == 102


def test_commit_shipment_to_transit(shipment_service, mock_db_service, mock_pools):
    shipments = shipment_service.commit_shipment(1)

    assert shipments.id == 1
    assert shipments.shipment_status == "Transit"


def test_commit_shipment_to_delivered(shipment_service, mock_db_service, mock_pools):
    shipments = shipment_service.commit_shipment(1)

    assert shipments.id == 1
    assert shipments.shipment_status == "Delivered"


def test_commit_shipment_not_found(shipment_service, mock_db_service, mock_pools):
    shipments = shipment_service.commit_shipment(4)

    assert shipments is None


def test_commit_shipment_archived(shipment_service, mock_db_service, mock_pools):
    shipments = shipment_service.commit_shipment(3)

    assert shipments is None
