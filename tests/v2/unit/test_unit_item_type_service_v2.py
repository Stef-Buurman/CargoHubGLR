from unittest.mock import Mock
import pytest
from app.models.v2.item_type import ItemType
from app.services.v2.model_services.item_type_service import ItemTypeService
from tests.test_globals import *


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def item_type_service(mock_db_service):
    """Fixture to create an ItemTypeService instance with the mocked DatabaseService."""
    service = ItemTypeService(
        True,
        [
            ItemType(
                id=1,
                name="Type A",
                description="",
                created_at="1993-07-28 13:43:32",
                updated_at="2022-05-12 08:54:35",
                is_archived=False,
            ),
            ItemType(
                id=2,
                name="Type B",
                description="",
                created_at="1993-07-28 13:43:32",
                updated_at="2022-05-12 08:54:35",
                is_archived=False,
            ),
            ItemType(
                id=3,
                name="Type C",
                description="",
                created_at="1993-07-28 13:43:32",
                updated_at="2022-05-12 08:54:35",
                is_archived=True,
            ),
        ],
        mock_db_service,
    )
    return service


def test_get_all_item_types(item_type_service, mock_db_service):
    mock_db_service.get_all.return_value = item_type_service.data
    item_types = item_type_service.get_all_item_types()

    assert len(item_types) == len(item_type_service.data)
    assert item_types[0].name == "Type A"
    assert mock_db_service.get_all.call_count == 1


def test_get_item_types(item_type_service):
    item_types = item_type_service.get_item_types()

    assert len(item_types) == 2
    assert all(not item_type.is_archived for item_type in item_types)


def test_get_item_type(item_type_service, mock_db_service):
    item_type_id = 1
    item_type = item_type_service.get_item_type(item_type_id)

    assert item_type.id == item_type_id
    assert mock_db_service.get.call_count == 0


def test_get_item_type_from_db(item_type_service, mock_db_service):
    mock_db_service.get.return_value = ItemType(
        id=4,
        name="Type D",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    item_type = item_type_service.get_item_type(4)

    assert item_type.id == 4
    assert mock_db_service.get.call_count == 1


def test_add_item_type(item_type_service, mock_db_service):
    new_item_type = ItemType(
        name="Type E",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    mock_db_service.insert.return_value = new_item_type

    result = item_type_service.add_item_type(new_item_type)

    assert mock_db_service.insert.call_count == 1
    assert new_item_type in item_type_service.data
    assert result.name == new_item_type.name


def test_update_item_type(item_type_service, mock_db_service):
    item_type_id = 1
    item_type = item_type_service.get_item_type(item_type_id)
    assert mock_db_service.get.call_count == 0
    assert item_type is not None

    updated_item_type = item_type.copy(update={"name": "Updated Type A"})
    mock_db_service.update.return_value = updated_item_type

    result = item_type_service.update_item_type(item_type_id, updated_item_type)

    assert mock_db_service.update.call_count == 1
    assert result.name == "Updated Type A"
    updated_item_type = item_type_service.get_item_type(item_type_id)
    assert updated_item_type.name == "Updated Type A"


def test_update_item_type_archived(item_type_service, mock_db_service):
    item_type_id = 1
    item_type = item_type_service.get_item_type(item_type_id)
    assert mock_db_service.get.call_count == 0
    assert item_type is not None

    mock_db_service.update.return_value = item_type.copy(update={"is_archived": True})

    updateditem_type = item_type_service.archive_item_type(item_type_id)
    assert updateditem_type.is_archived == True
    assert mock_db_service.update.call_count == 1

    updated_item_type = item_type.copy(update={"name": "naame"})

    result = item_type_service.update_item_type(item_type_id, updated_item_type)

    assert mock_db_service.update.call_count == 1
    assert result is None
    updated_item_type = item_type_service.get_item_type(item_type_id)
    assert updated_item_type.is_archived


def test_archive_item_type(item_type_service, mock_db_service):
    item_type_id = 1
    item_type = item_type_service.get_item_type(item_type_id)
    mock_db_service.update.return_value = item_type

    result = item_type_service.archive_item_type(item_type_id)

    assert mock_db_service.update.call_count == 1
    assert result.is_archived
    new_item_type = item_type_service.get_item_type(item_type_id)
    assert new_item_type.is_archived


def test_archive_item_type_not_found(item_type_service, mock_db_service):
    item_type_id = non_existent_id
    result = item_type_service.archive_item_type(item_type_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_item_type(item_type_service, mock_db_service):
    item_type_id = 1
    item_type = item_type_service.get_item_type(item_type_id)
    mock_db_service.update.return_value = item_type

    result = item_type_service.unarchive_item_type(item_type_id)

    assert mock_db_service.update.call_count == 1
    assert not result.is_archived
    new_item_type = item_type_service.get_item_type(item_type_id)
    assert not new_item_type.is_archived


def test_unarchive_item_type_not_found(item_type_service, mock_db_service):
    item_type_id = non_existent_id
    result = item_type_service.unarchive_item_type(item_type_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_item_type_archived(item_type_service):
    assert item_type_service.is_item_type_archived(1) is False
    assert item_type_service.is_item_type_archived(3) is True
    assert item_type_service.is_item_type_archived(99) is None
