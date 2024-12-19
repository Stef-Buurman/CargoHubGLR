from unittest.mock import Mock
import pytest
from app.models.v2.location import Location
from app.services.v2.model_services.location_service import LocationService
from tests.test_globals import *

TEST_LOCATIONS = [
    Location(
        id=1,
        warehouse_id=1,
        code="A.1.0",
        name="Row: A, Rack: 1, Shelf: 0",
        created_at="1992-05-15 03:21:32",
        updated_at="1992-05-15 03:21:32",
        is_archived=False,
    ),
    Location(
        id=2,
        warehouse_id=2,
        code="A.1.1",
        name="Row: A, Rack: 1, Shelf: 1",
        created_at="1992-05-15 03:21:32",
        updated_at="1992-05-15 03:21:32",
        is_archived=False,
    ),
    Location(
        id=3,
        warehouse_id=1,
        code="A.2.0",
        name="Row: A, Rack: 2, Shelf: 0",
        created_at="1992-05-15 03:21:32",
        updated_at="1992-05-15 03:21:32",
        is_archived=True,
    ),
]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def location_service(mock_db_service):
    """Fixture to create an LocationService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_LOCATIONS
    service = LocationService(mock_db_service)
    return service


def test_get_all_locations(location_service, mock_db_service):
    locations = location_service.get_all_locations()

    assert len(locations) == len(location_service.data)
    assert locations[0].name == "Row: A, Rack: 1, Shelf: 0"
    assert mock_db_service.get_all.call_count == 2


def test_get_locations(location_service):
    locations = location_service.get_locations()

    assert len(locations) == 2
    assert all(not location.is_archived for location in locations)


def test_get_location(location_service, mock_db_service):
    location_id = 1
    location = location_service.get_location(location_id)

    assert location.id == location_id
    assert mock_db_service.get.call_count == 0


def test_get_location_not_found(location_service, mock_db_service):
    mock_db_service.get.return_value = None
    location = location_service.get_location(non_existent_id)

    assert location is None
    assert mock_db_service.get.call_count == 1


def test_get_locations_in_warehouse(location_service):
    warehouse_id = 1
    locations = location_service.get_locations_in_warehouse(warehouse_id)

    assert len(locations) == 2
    assert all(location.warehouse_id == warehouse_id for location in locations)


def test_get_locations_in_warehouse_not_found(location_service):
    locations = location_service.get_locations_in_warehouse(non_existent_id)

    assert len(locations) == 0


def test_get_location_from_db(location_service, mock_db_service):
    mock_db_service.get.return_value = Location(
        id=non_existent_id,
        warehouse_id=1,
        code="A.1.0",
        name="Row: A, Rack: 1, Shelf: 0",
        created_at="1992-05-15 03:21:32",
        updated_at="1992-05-15 03:21:32",
    )

    location = location_service.get_location(non_existent_id)

    assert location.id == non_existent_id
    assert location.name == "Row: A, Rack: 1, Shelf: 0"
    assert mock_db_service.get.call_count == 1


def test_get_location_from_db_not_found(location_service, mock_db_service):
    mock_db_service.get.return_value = None

    location = location_service.get_location(non_existent_id)

    assert location is None
    assert mock_db_service.get.call_count == 1


def test_add_location(location_service, mock_db_service):
    new_location = Location(
        id=4,
        warehouse_id=1,
        code="A.2.1",
        name="Row: A, Rack: 2, Shelf: 1",
        created_at="1992-05-15 03:21:32",
        updated_at="1992-05-15 03:21:32",
    )
    mock_db_service.insert.return_value = new_location

    result = location_service.add_location(new_location)

    assert mock_db_service.insert.call_count == 1
    assert new_location in location_service.data
    assert result.name == new_location.name
    assert result.code == new_location.code


def test_update_location(location_service, mock_db_service):
    location_id = 1
    location = location_service.get_location(location_id)
    assert mock_db_service.get.call_count == 0
    assert location is not None

    updated_location = location.copy(
        update={"name": "Row: A, Rack: 1, Shelf: 0 Updated"}
    )
    mock_db_service.update.return_value = updated_location

    result = location_service.update_location(location_id, updated_location)

    assert mock_db_service.update.call_count == 1
    assert result.name == "Row: A, Rack: 1, Shelf: 0 Updated"
    updated_location = location_service.get_location(location_id)
    assert updated_location.name == "Row: A, Rack: 1, Shelf: 0 Updated"


def test_update_location_archived(location_service, mock_db_service):
    location_id = 1
    location = location_service.get_location(location_id)
    assert mock_db_service.get.call_count == 0
    assert location is not None

    mock_db_service.update.return_value = location.copy(update={"is_archived": True})

    updatedlocation = location_service.archive_location(location_id)
    assert updatedlocation.is_archived == True
    assert mock_db_service.update.call_count == 1

    updated_location = location.copy(update={"name": "naame"})

    result = location_service.update_location(location_id, updated_location)

    assert mock_db_service.update.call_count == 1
    assert result is None
    updated_location = location_service.get_location(location_id)
    assert updated_location.is_archived


def test_is_location_archived(location_service, mock_db_service):
    location_id = 3
    location = location_service.get_location(location_id)
    assert location.is_archived

    result = location_service.is_location_archived(location_id)

    assert result
    assert mock_db_service.get.call_count == 0


def test_is_location_archived_not_found(location_service, mock_db_service):
    result = location_service.is_location_archived(non_existent_id)

    assert result is None
    assert mock_db_service.get.call_count == 0


def test_archive_location(location_service, mock_db_service):
    location_id = 1
    location = location_service.get_location(location_id)
    mock_db_service.update.return_value = location

    result = location_service.archive_location(location_id)

    assert mock_db_service.update.call_count == 1
    assert result.is_archived
    new_location = location_service.get_location(location_id)
    assert new_location.is_archived


def test_archive_location_not_found(location_service, mock_db_service):
    location_id = non_existent_id
    result = location_service.archive_location(location_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_location(location_service, mock_db_service):
    location_id = 1
    location = location_service.get_location(location_id)
    location.is_archived = True
    mock_db_service.update.return_value = location

    result = location_service.unarchive_location(location_id)

    assert mock_db_service.update.call_count == 1
    assert not result.is_archived
    new_location = location_service.get_location(location_id)
    assert not new_location.is_archived


def test_unarchive_location_not_found(location_service, mock_db_service):
    location_id = non_existent_id
    result = location_service.unarchive_location(location_id)

    assert result is None
    assert mock_db_service.update.call_count == 0
