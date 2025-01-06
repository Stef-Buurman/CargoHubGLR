from unittest.mock import Mock
import pytest
from app.models.v2.warehouse import Warehouse
from app.services.v2.model_services.warehouse_service import WarehouseService
from tests.test_globals import *


TEST_WAREHOUSES = [
    Warehouse(
        id=1,
        code="YQZZNL56",
        name="Heemskerk cargo hub",
        address="Karlijndreef 281",
        zip="4002 AS",
        city="Heemskerk",
        province="Friesland",
        country="NL",
        contact_name="Fem Keijzer",
        contact_phone="(078) 0013363",
        contact_email="blamore@example.net",
        created_at="1983-04-13 04:59:55",
        updated_at="2007-02-08 20:11:00",
        is_archived=False,
    ),
    Warehouse(
        id=2,
        code="GIOMNL90",
        name="Petten longterm hub",
        address="Owenweg 731",
        zip="4615 RB",
        city="Petten",
        province="Noord-Holland",
        country="NL",
        contact_name="Maud Adryaens",
        contact_phone="+31836 752702",
        contact_email="nickteunissen@example.com",
        created_at="2008-02-22 19:55:39",
        updated_at="2009-08-28 23:15:50",
        is_archived=False,
    ),
    Warehouse(
        id=3,
        code="VCKINLLK",
        name="Naaldwijk distribution hub",
        address="Izesteeg 807",
        zip="1636 KI",
        city="Naaldwijk",
        province="Utrecht",
        country="NL",
        contact_name="Frederique van Wallaert",
        contact_phone="(009) 4870289",
        contact_email="jelle66@example.net",
        created_at="2001-05-11 10:43:52",
        updated_at="2017-12-19 14:32:38",
        is_archived=True,
    ),
]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def warehouse_service(mock_db_service):
    """Fixture to create an WarehouseService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_WAREHOUSES
    service = WarehouseService(mock_db_service)
    return service


def test_get_all_warehouses(warehouse_service, mock_db_service):
    warehouses = warehouse_service.get_all_warehouses()

    assert len(warehouses) == len(warehouse_service.data)
    assert warehouses[0].name == "Heemskerk cargo hub"
    assert mock_db_service.get_all.call_count == 2


def test_get_warehouses(warehouse_service):
    warehouses = warehouse_service.get_warehouses()

    assert len(warehouses) == 2
    assert all(not warehouse.is_archived for warehouse in warehouses)


def test_get_warehouse(warehouse_service, mock_db_service):
    warehouse_id = 1
    warehouse = warehouse_service.get_warehouse(warehouse_id)

    assert warehouse.id == warehouse_id
    assert mock_db_service.get.call_count == 0


def test_get_warehouse_not_found(warehouse_service, mock_db_service):
    mock_db_service.get.return_value = None
    assert warehouse_service.get_warehouse(non_existent_id) is None
    assert mock_db_service.get.call_count == 1


def test_get_warehouse_from_db(warehouse_service, mock_db_service):
    warehouse_from_db = Warehouse(
        id=5,
        code="VCKINLLK",
        name="Naaldwijk distribution hub",
        address="Izesteeg 807",
        zip="1636 KI",
        city="Naaldwijk",
        province="Utrecht",
        country="NL",
        contact_name="Frederique van Wallaert",
        contact_phone="(009) 4870289",
        contact_email="jelle66@example.net",
        created_at="2001-05-11 10:43:52",
        updated_at="2017-12-19 14:32:38",
        is_archived=True,
    )
    mock_db_service.get.return_value = warehouse_from_db

    warehouse = warehouse_service.get_warehouse(5)

    assert warehouse.id == 5
    assert mock_db_service.get.call_count == 1
    assert warehouse == warehouse_from_db


def test_add_warehouse(warehouse_service, mock_db_service):
    warehouse = Warehouse(
        id=3,
        code="VCKINLLK",
        name="Naaldwijk distribution hub",
        address="Izesteeg 807",
        zip="1636 KI",
        city="Naaldwijk",
        province="Utrecht",
        country="NL",
        contact_name="Frederique van Wallaert",
        contact_phone="(009) 4870289",
        contact_email="jelle66@example.net",
        created_at="2001-05-11 10:43:52",
        updated_at="2017-12-19 14:32:38",
    )
    mock_db_service.insert.return_value = warehouse.model_copy(update={"id": 4})
    result = warehouse_service.add_warehouse(warehouse)

    assert result.id == 4
    assert mock_db_service.insert.call_count == 1


def test_update_warehouse(warehouse_service, mock_db_service):
    warehouse = Warehouse(
        id=1,
        code="YQZZNL56",
        name="Heemskerk cargo hub",
        address="Karlijndreef 281",
        zip="4002 AS",
        city="Heemskerk",
        province="Friesland",
        country="NL",
        contact_name="Fem Keijzer",
        contact_phone="(078) 0013363",
        contact_email="test@mail.com",
        created_at="1983-04-13 04:59:55",
        updated_at="2007-02-08 20:11:00",
    )
    mock_db_service.update.return_value = warehouse
    result = warehouse_service.update_warehouse(warehouse.id, warehouse)

    assert result.id == warehouse.id
    assert warehouse.model_copy(update={"updated_at": result.updated_at}) == result
    assert mock_db_service.update.call_count == 1


def test_update_warehouse_archived(warehouse_service, mock_db_service):
    warehouse = Warehouse(
        id=3,
        code="YQZZNL56",
        name="Heemskerk cargo hub",
        address="Karlijndreef 281",
        zip="4002 AS",
        city="Heemskerk",
        province="Friesland",
        country="NL",
        contact_name="Fem Keijzer",
        contact_phone="(078) 0013363",
        contact_email="test@mail.com",
        created_at="1983-04-13 04:59:55",
        updated_at="2007-02-08 20:11:00",
        is_archived=True,
    )
    result = warehouse_service.update_warehouse(warehouse.id, warehouse)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_warehouse_archived(warehouse_service, mock_db_service):
    warehouse_id = 3
    warehouse = warehouse_service.get_warehouse(warehouse_id)
    assert warehouse is not None

    assert warehouse_service.is_warehouse_archived(warehouse_id)
    assert mock_db_service.get.call_count == 0


def test_is_warehouse_archived_not_found(warehouse_service, mock_db_service):
    assert not warehouse_service.is_warehouse_archived(non_existent_id)
    assert mock_db_service.get.call_count == 0


def test_archive_warehouse(warehouse_service, mock_db_service):
    warehouse_id = 1
    warehouse = warehouse_service.get_warehouse(warehouse_id)
    assert warehouse is not None

    mock_db_service.update.return_value = warehouse.copy(update={"is_archived": True})

    result = warehouse_service.archive_warehouse(warehouse_id)

    assert result.is_archived == True
    assert mock_db_service.update.call_count == 1


def test_archive_warehouse_not_found(warehouse_service, mock_db_service):
    result = warehouse_service.archive_warehouse(non_existent_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_warehouse(warehouse_service, mock_db_service):
    warehouse_id = 1
    warehouse = warehouse_service.get_warehouse(warehouse_id)
    assert warehouse is not None

    warehouse.is_archived = True
    mock_db_service.update.return_value = warehouse

    result = warehouse_service.unarchive_warehouse(warehouse_id)

    assert not result.is_archived
    assert mock_db_service.update.call_count == 1


def test_unarchive_warehouse_not_found(warehouse_service, mock_db_service):
    result = warehouse_service.unarchive_warehouse(non_existent_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_warehouse_archived(warehouse_service):
    assert warehouse_service.is_warehouse_archived(1) is False
    assert warehouse_service.is_warehouse_archived(3) is True
    assert warehouse_service.is_warehouse_archived(99) is None
