from unittest.mock import MagicMock
import pytest
from app.models.v2.ItemInObject import ItemInObject
from app.models.v2.order import Order
from app.models.v2.shipment import Shipment
from app.services.v2.model_services.order_service import OrderService
from tests.test_globals import *

TEST_ORDERS = [
    Order(
        id=1,
        source_id=1,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #1",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=1,
        ship_to=1,
        bill_to=1,
        shipment_id=1,
        total_amount=100.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    Order(
        id=2,
        source_id=2,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #2",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=2,
        ship_to=2,
        bill_to=2,
        shipment_id=2,
        total_amount=200.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    Order(
        id=3,
        source_id=3,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #3",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=1,
        ship_to=1,
        bill_to=1,
        shipment_id=3,
        total_amount=300.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
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

    shipment_pool_mock = MagicMock()
    data_provider_mock.fetch_shipment_pool.return_value = shipment_pool_mock

    return mock_db_service, mock_conn, mock_cursor, data_provider_mock


@pytest.fixture
def mock_pools(mock_db_service, mock_get_connection):
    """Fixture to create a mocked PoolsService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )

    shipment_pool_mock = MagicMock()
    data_provider_mock.fetch_shipment_pool.return_value = shipment_pool_mock

    shipment_pool_mock.is_shipment_archived.return_value = False

    client_pool_mock = MagicMock()
    data_provider_mock.fetch_client_pool.return_value = client_pool_mock

    client_pool_mock.is_client_archived.return_value = False

    warehouse_pool_mock = MagicMock()
    data_provider_mock.fetch_warehouse_pool.return_value = warehouse_pool_mock

    warehouse_pool_mock.is_warehouse_archived.return_value = False

    item_pool_mock = MagicMock()
    data_provider_mock.fetch_item_pool.return_value = item_pool_mock

    item_pool_mock.is_item_archived.return_value = False

    return shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock


@pytest.fixture
def order_service(mock_db_service, mock_get_connection):
    """Fixture to create an OrderService instance with the mocked DatabaseService."""
    mock_get_connection, mock_conn, mock_cursor, data_provider_mock = (
        mock_get_connection
    )
    mock_db_service.get_all.return_value = TEST_ORDERS
    mock_cursor.fetchall.return_value = test_item_in_object
    service = OrderService(mock_db_service, data_provider_mock, True)
    return service


def test_get_all_orders(order_service, mock_db_service, mock_get_connection):

    orders = order_service.get_all_orders()

    assert len(orders) == len(order_service.data)
    assert orders[0].reference == "Order #1"
    assert mock_db_service.get_all.call_count == 2


def test_get_orders(order_service):
    orders = order_service.get_orders()

    assert len(orders) == 2
    assert all(not order.is_archived for order in orders)


def test_get_order(order_service):
    order = order_service.get_order(1)

    assert order is TEST_ORDERS[0]


def test_get_order_from_db(order_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection

    order_to_return = Order(
        id=4,
        source_id=4,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #3",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=1,
        ship_to=1,
        bill_to=1,
        shipment_id=3,
        total_amount=300.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=True,
    )

    mock_cursor.description = pydantic_models_keys_to_tuple_array(order_to_return)

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(order_to_return)

    order = order_service.get_order(4)

    mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert order.id == order_to_return.id


def test_get_items_in_order(
    order_service,
):
    items = order_service.get_items_in_order(1)

    assert len(items) == 2
    assert items[0].item_id == test_item_in_object[0][0]
    assert items[1].item_id == test_item_in_object[1][0]


def test_get_items_in_order_not_found(order_service):
    items = order_service.get_items_in_order(4)

    assert items == None


def test_get_orders_in_shipment(order_service):
    orders = order_service.get_orders_in_shipment(1)

    assert len(orders) == 1
    assert orders[0].shipment_id == TEST_ORDERS[0].shipment_id


def test_get_orders_for_client(order_service):
    orders = order_service.get_orders_for_client(1)

    assert len(orders) == 2
    assert all(order.ship_to == 1 for order in orders)


def test_add_order(order_service, mock_db_service, mock_get_connection, mock_pools):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )

    shipment_pool_mock.is_shipment_archived.return_value = False
    client_pool_mock.is_client_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = False
    new_order = Order(
        source_id=4,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #4",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=4,
        ship_to=4,
        bill_to=4,
        shipment_id=4,
        total_amount=400.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
        items=[
            ItemInObject(item_id="p10011", amount=1),
            ItemInObject(item_id="p10012", amount=2),
        ],
    )

    result = order_service.add_order(new_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 4
    assert new_order in order_service.data
    assert result.source_id == new_order.source_id


def test_add_order_has_archived_entities_shipment(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )

    shipment_pool_mock.is_shipment_archived.return_value = True
    new_order = Order(
        source_id=4,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #4",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=4,
        ship_to=4,
        bill_to=4,
        shipment_id=4,
        total_amount=400.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
        items=[
            ItemInObject(item_id="p10011", amount=1),
            ItemInObject(item_id="p10012", amount=2),
        ],
    )

    result = order_service.add_order(new_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert new_order not in order_service.data


def test_add_order_has_archived_entities_client(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )

    shipment_pool_mock.is_shipment_archived.return_value = False
    client_pool_mock.is_client_archived.return_value = True
    new_order = Order(
        source_id=4,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #4",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=4,
        ship_to=4,
        bill_to=4,
        shipment_id=4,
        total_amount=400.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
        items=[
            ItemInObject(item_id="p10011", amount=1),
            ItemInObject(item_id="p10012", amount=2),
        ],
    )

    result = order_service.add_order(new_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert new_order not in order_service.data


def test_add_order_has_archived_entities_warehouse(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )

    shipment_pool_mock.is_shipment_archived.return_value = False
    client_pool_mock.is_client_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = True
    new_order = Order(
        source_id=4,
        order_date="2022-05-12 08:54:35",
        request_date="2022-05-12 08:54:35",
        reference="Order #4",
        reference_extra="",
        order_status="Pending",
        notes="",
        shipping_notes="",
        picking_notes="",
        warehouse_id=4,
        ship_to=4,
        bill_to=4,
        shipment_id=4,
        total_amount=400.0,
        total_discount=0.0,
        total_tax=0.0,
        total_surcharge=0.0,
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
        items=[
            ItemInObject(item_id="p10011", amount=1),
            ItemInObject(item_id="p10012", amount=2),
        ],
    )

    result = order_service.add_order(new_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    assert new_order not in order_service.data


def test_update_order(order_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    order_id = 1
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"order_status": "Shipped", "created_at": None})
    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(updated_order)

    result = order_service.update_order(order_id, updated_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.order_status == "Shipped"
    updated_order = order_service.get_order(order_id)
    assert updated_order.order_status == "Shipped"


def test_update_order_archived_client(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    client_pool_mock.is_client_archived.return_value = True
    shipment_pool_mock.is_shipment_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = False
    order_id = 2
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"ship_to": order.ship_to + 1})

    result = order_service.update_order(order_id, updated_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_order_archived_client_bill_to(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    client_pool_mock.is_client_archived.return_value = True
    shipment_pool_mock.is_shipment_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = False
    order_id = 2
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"bill_to": order.bill_to + 1})

    result = order_service.update_order(order_id, updated_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_order_archived_warehouse(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    warehouse_pool_mock.is_warehouse_archived.return_value = True
    shipment_pool_mock.is_shipment_archived.return_value = False
    order_id = 2
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"warehouse_id": order.warehouse_id + 1})

    result = order_service.update_order(order_id, updated_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_order_archived_shipment(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    shipment_pool_mock.is_shipment_archived.return_value = True
    order_id = 2
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"shipment_id": order.shipment_id + 1})

    result = order_service.update_order(order_id, updated_order)

    assert shipment_pool_mock.is_shipment_archived.call_count == 1

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None


def test_update_order_archived(order_service, mock_db_service, mock_get_connection):
    order_id = 3
    order = order_service.get_order(order_id)
    assert order is not None

    updated_order = order.copy(update={"order_status": "Shipped"})

    result = order_service.archive_order(order_id)
    assert result.is_archived == True
    assert mock_db_service.get_connection().__enter__().execute.call_count == 2

    result = order_service.update_order(order_id, updated_order)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result is None
    updated_order = order_service.get_order(order_id)
    assert updated_order.is_archived


def test_update_items_in_order(
    order_service, mock_db_service, mock_get_connection, mock_pools
):

    order_id = 1
    items = order_service.get_items_in_order(order_id)
    assert items is not None

    updated_items = [
        ItemInObject(item_id="p10011", amount=2),
        ItemInObject(item_id="p10012", amount=3),
    ]

    result = order_service.update_items_in_order(order_id, updated_items)
    print(result)
    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result is not None
    assert result.items[0].amount == 2
    assert result.items[1].amount == 3


def test_update_items_in_order_archived(
    order_service, mock_db_service, mock_get_connection
):
    order_id = 3
    items = order_service.get_items_in_order(order_id)
    assert items is not None

    updated_items = [
        ItemInObject(item_id="p10011", amount=2),
        ItemInObject(item_id="p10012", amount=3),
    ]

    result = order_service.update_items_in_order(order_id, updated_items)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result is None
    updated_order = order_service.get_order(order_id)
    assert updated_order.is_archived


def test_update_orders_in_shipment(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    shipment_id = 1
    orders = order_service.get_orders_in_shipment(shipment_id)
    assert orders is not None

    updated_orders = [
        Order(
            id=1,
            source_id=1,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            reference="Order #1",
            reference_extra="",
            order_status="",
            notes="",
            shipping_notes="",
            picking_notes="",
            warehouse_id=1,
            ship_to=1,
            bill_to=1,
            shipment_id=1,
            total_amount=100.0,
            total_discount=0.0,
            total_tax=0.0,
            total_surcharge=0.0,
            created_at="1993-07-28 13:43:32",
            updated_at="2022-05-12 08:54:35",
            is_archived=False,
        ),
        Order(
            id=2,
            source_id=2,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            reference="Order #2",
            reference_extra="",
            order_status="",
            notes="",
            shipping_notes="",
            picking_notes="",
            warehouse_id=2,
            ship_to=2,
            bill_to=2,
            shipment_id=2,
            total_amount=200.0,
            total_discount=0.0,
            total_tax=0.0,
            total_surcharge=0.0,
            created_at="1993-07-28 13:43:32",
            updated_at="2022-05-12 08:54:35",
            is_archived=False,
            items=[
                ItemInObject(item_id="p10011", amount=1),
                ItemInObject(item_id="p10012", amount=2),
            ],
        ),
    ]

    result = order_service.update_orders_in_shipment(shipment_id, updated_orders)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 8
    assert result is not None
    assert result[0].order_status == "Packed"
    assert result[1].order_status == "Packed"


def test_archive_order(order_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    order_id = 1
    order = order_service.get_order(order_id)
    assert order is not None

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(order)

    result = order_service.archive_order(order_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.is_archived == True


def test_archive_order_not_found(order_service, mock_db_service, mock_get_connection):
    result = order_service.archive_order(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_is_order_archived(order_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    order_id = 3
    order = order_service.get_order(order_id)
    assert order is not None

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(order)

    result = order_service.is_order_archived(order_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == True


def test_is_order_archived_not_found(
    order_service, mock_db_service, mock_get_connection
):
    result = order_service.is_order_archived(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_unarchive_order(order_service, mock_db_service, mock_get_connection):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    order_id = 1
    order = order_service.get_order(order_id)
    assert order is not None

    mock_cursor.fetchone.return_value = pydantic_models_value_to_tuple(order)

    result = order_service.unarchive_order(order_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.is_archived == False


def test_unarchive_order_not_found(order_service, mock_db_service, mock_get_connection):
    result = order_service.unarchive_order(non_existent_id)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_check_if_order_transit(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    shipment_pool_mock.get_shipments_for_order.return_value = [
        Shipment(
            id=1,
            order_id=1,
            source_id=1,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            shipment_date="2022-05-13 08:54:35",
            shipment_type="Standard",
            shipment_status="Transit",
            notes="Handle with care",
            carrier_code="UPS",
            carrier_description="United Parcel Service",
            service_code="Ground",
            payment_type="Prepaid",
            transfer_mode="Air",
            total_package_count=2,
            total_package_weight=5.0,
            created_at="2022-05-12 08:54:35",
            updated_at="2022-05-12 08:54:35",
        )
    ]

    result = order_service.check_if_order_transit(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.order_status == "Shipped"


def test_check_if_order_transit_not_found(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    shipment_pool_mock.get_shipments_for_order.return_value = [
        Shipment(
            id=1,
            order_id=1,
            source_id=1,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            shipment_date="2022-05-13 08:54:35",
            shipment_type="Standard",
            shipment_status="x",
            notes="Handle with care",
            carrier_code="UPS",
            carrier_description="United Parcel Service",
            service_code="Ground",
            payment_type="Prepaid",
            transfer_mode="Air",
            total_package_count=2,
            total_package_weight=5.0,
            created_at="2022-05-12 08:54:35",
            updated_at="2022-05-12 08:54:35",
        )
    ]

    result = order_service.check_if_order_transit(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


def test_check_if_order_delivered(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )

    shipment_pool_mock.is_shipment_archived.return_value = False
    client_pool_mock.is_client_archived.return_value = False
    warehouse_pool_mock.is_warehouse_archived.return_value = False
    shipment_pool_mock.get_shipments_for_order.return_value = [
        Shipment(
            id=1,
            order_id=1,
            source_id=1,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            shipment_date="2022-05-13 08:54:35",
            shipment_type="Standard",
            shipment_status="Delivered",
            notes="Handle with care",
            carrier_code="UPS",
            carrier_description="United Parcel Service",
            service_code="Ground",
            payment_type="Prepaid",
            transfer_mode="Air",
            total_package_count=2,
            total_package_weight=5.0,
            created_at="2022-05-12 08:54:35",
            updated_at="2022-05-12 08:54:35",
        )
    ]

    result = order_service.check_if_order_delivered(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 2
    assert result.order_status == "Delivered"


def test_check_if_order_delivered_not_found(
    order_service, mock_db_service, mock_get_connection, mock_pools
):
    mock_db_service, mock_conn, mock_cursor, data_provider_mock = mock_get_connection
    shipment_pool_mock, client_pool_mock, warehouse_pool_mock, item_pool_mock = (
        mock_pools
    )
    shipment_pool_mock.get_shipments_for_order.return_value = [
        Shipment(
            id=1,
            order_id=1,
            source_id=1,
            order_date="2022-05-12 08:54:35",
            request_date="2022-05-12 08:54:35",
            shipment_date="2022-05-13 08:54:35",
            shipment_type="Standard",
            shipment_status="x",
            notes="Handle with care",
            carrier_code="UPS",
            carrier_description="United Parcel Service",
            service_code="Ground",
            payment_type="Prepaid",
            transfer_mode="Air",
            total_package_count=2,
            total_package_weight=5.0,
            created_at="2022-05-12 08:54:35",
            updated_at="2022-05-12 08:54:35",
        )
    ]

    result = order_service.check_if_order_delivered(1)

    assert mock_db_service.get_connection().__enter__().execute.call_count == 1
    assert result == None


# assert order.id == 4
# assert order.source_id == 4
# assert order.order_date == "2022-05-12 08:54:35"
# assert order.request_date == "2022-05-12 08:54:35"
# assert order.reference == "Order #4"
# assert order.reference_extra == ""
# assert order.order_status == "Pending"
# assert order.notes == ""
# assert order.shipping_notes == ""
# assert order.picking_notes == ""
# assert order.warehouse_id == 4
# assert order.ship_to == 4
# assert order.bill_to == 4
# assert order.shipment_id == 4
# assert order.total_amount == 400.0
# assert order.total_discount == 0.0
# assert order.total_tax == 0.0
# assert order.total_surcharge == 0.0
# assert order.created_at == "1993-07-28 13:43:32"
# assert order.updated_at == "2022-05-12 08:54:35"
# assert order.is_archived == False
# assert mock_db_service.get_one.call_count == 1
# assert mock_db_service.get_one.assert_called_with(4)


# def test_get_order_not_found(order_service, mock_db_service):
#     mock_db_service.get_one.return_value = None
#     order = order_service.get_order(5)

#     assert order is None
#     assert mock_db_service.get_one.call_count == 1
#     assert mock_db_service.get_one.assert_called_with(5)


# def test_get_orders_in_warehouse(order_service):
#     warehouse_id = 1
#     orders = order_service.get_orders_in_warehouse(warehouse_id)

#     assert len(orders) == 2
#     assert all(order.warehouse_id == warehouse_id for order in orders)


# def test_get_orders_in_warehouse_not_found(order_service):
#     orders = order_service.get_orders_in_warehouse(4)

#     assert len(orders) == 0
