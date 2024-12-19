from unittest.mock import Mock
import pytest
from app.models.v2.item_line import ItemLine
from app.services.v2.model_services.item_line_service import ItemLineService
from tests.test_globals import *


TEST_ITEM_LINES = [
    ItemLine(
        id=1,
        name="Type A",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    ItemLine(
        id=2,
        name="Type B",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    ItemLine(
        id=3,
        name="Type C",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=True,
    ),
]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def item_line_service(mock_db_service):
    """Fixture to create an ItemLineService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_ITEM_LINES
    service = ItemLineService(mock_db_service)
    return service


def test_get_all_item_lines(item_line_service, mock_db_service):
    item_lines = item_line_service.get_all_item_lines()

    assert len(item_lines) == len(item_line_service.data)
    assert item_lines[0].name == "Type A"
    assert mock_db_service.get_all.call_count == 2


def test_get_item_lines(item_line_service):
    item_lines = item_line_service.get_item_lines()

    assert len(item_lines) == 2
    assert all(not item_line.is_archived for item_line in item_lines)


def test_get_item_line(item_line_service, mock_db_service):
    item_line_id = 1
    item_line = item_line_service.get_item_line(item_line_id)

    assert item_line.id == item_line_id
    assert mock_db_service.get.call_count == 0


def test_get_item_line_from_db(item_line_service, mock_db_service):
    mock_db_service.get.return_value = ItemLine(
        id=4,
        name="Type D",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    item_line = item_line_service.get_item_line(4)

    assert item_line.id == 4
    assert mock_db_service.get.call_count == 1


def test_add_item_line(item_line_service, mock_db_service):
    new_item_line = ItemLine(
        name="Type E",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    mock_db_service.insert.return_value = new_item_line

    result = item_line_service.add_item_line(new_item_line)

    assert mock_db_service.insert.call_count == 1
    assert new_item_line in item_line_service.data
    assert result.name == new_item_line.name


def test_update_item_line(item_line_service, mock_db_service):
    item_line_id = 1
    item_line = item_line_service.get_item_line(item_line_id)
    assert mock_db_service.get.call_count == 0
    assert item_line is not None

    updated_item_line = item_line.copy(update={"name": "Updated Type A"})
    mock_db_service.update.return_value = updated_item_line

    result = item_line_service.update_item_line(item_line_id, updated_item_line)

    assert mock_db_service.update.call_count == 1
    assert result.name == "Updated Type A"
    updated_item_line = item_line_service.get_item_line(item_line_id)
    assert updated_item_line.name == "Updated Type A"


def test_update_item_line_archived(item_line_service, mock_db_service):
    item_line_id = 1
    item_line = item_line_service.get_item_line(item_line_id)
    assert mock_db_service.get.call_count == 0
    assert item_line is not None

    mock_db_service.update.return_value = item_line.copy(update={"is_archived": True})

    updateditem_line = item_line_service.archive_item_line(item_line_id)
    assert updateditem_line.is_archived == True
    assert mock_db_service.update.call_count == 1

    updated_item_line = item_line.copy(update={"name": "naame"})

    result = item_line_service.update_item_line(item_line_id, updated_item_line)

    assert mock_db_service.update.call_count == 1
    assert result is None
    updated_item_line = item_line_service.get_item_line(item_line_id)
    assert updated_item_line.is_archived


def test_archive_item_line(item_line_service, mock_db_service):
    item_line_id = 1
    item_line = item_line_service.get_item_line(item_line_id)
    mock_db_service.update.return_value = item_line

    result = item_line_service.archive_item_line(item_line_id)

    assert mock_db_service.update.call_count == 1
    assert result.is_archived
    new_item_line = item_line_service.get_item_line(item_line_id)
    assert new_item_line.is_archived


def test_archive_item_line_not_found(item_line_service, mock_db_service):
    item_line_id = non_existent_id
    result = item_line_service.archive_item_line(item_line_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_item_line(item_line_service, mock_db_service):
    item_line_id = 1
    item_line = item_line_service.get_item_line(item_line_id)
    mock_db_service.update.return_value = item_line

    result = item_line_service.unarchive_item_line(item_line_id)

    assert mock_db_service.update.call_count == 1
    assert not result.is_archived
    new_item_line = item_line_service.get_item_line(item_line_id)
    assert not new_item_line.is_archived


def test_unarchive_item_line_not_found(item_line_service, mock_db_service):
    item_line_id = non_existent_id
    result = item_line_service.unarchive_item_line(item_line_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_item_line_archived(item_line_service):
    assert item_line_service.is_item_line_archived(1) is False
    assert item_line_service.is_item_line_archived(3) is True
    assert item_line_service.is_item_line_archived(99) is None
