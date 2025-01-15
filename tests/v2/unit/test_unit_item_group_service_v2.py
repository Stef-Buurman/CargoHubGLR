from unittest.mock import Mock
import pytest
from app.models.v2.item_group import ItemGroup
from app.services.v2.model_services.item_group_service import ItemGroupService
from tests.test_globals import *


TEST_ITEM_GROUPS = [
    ItemGroup(
        id=1,
        name="Type A",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    ItemGroup(
        id=2,
        name="Type B",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    ),
    ItemGroup(
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
def item_group_service(mock_db_service):
    """Fixture to create an ItemGroupService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_ITEM_GROUPS
    service = ItemGroupService(mock_db_service, True)
    return service


def test_get_all_item_groups(item_group_service, mock_db_service):
    item_groups = item_group_service.get_all_item_groups()

    assert len(item_groups) == len(item_group_service.data)
    assert item_groups[0].name == "Type A"
    assert mock_db_service.get_all.call_count == 2


def test_get_item_groups(item_group_service):
    item_groups = item_group_service.get_item_groups()

    assert len(item_groups) == 2
    assert all(not item_group.is_archived for item_group in item_groups)


def test_get_item_group(item_group_service, mock_db_service):
    item_group_id = 1
    item_group = item_group_service.get_item_group(item_group_id)

    assert item_group.id == item_group_id
    assert mock_db_service.get.call_count == 0


def test_get_item_group_from_db(item_group_service, mock_db_service):
    mock_db_service.get.return_value = ItemGroup(
        id=4,
        name="Type D",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    item_group = item_group_service.get_item_group(4)

    assert item_group.id == 4
    assert mock_db_service.get.call_count == 1


def test_add_item_group(item_group_service, mock_db_service):
    new_item_group = ItemGroup(
        name="Type E",
        description="",
        created_at="1993-07-28 13:43:32",
        updated_at="2022-05-12 08:54:35",
        is_archived=False,
    )
    mock_db_service.insert.return_value = new_item_group

    result = item_group_service.add_item_group(new_item_group)

    assert mock_db_service.insert.call_count == 1
    assert new_item_group in item_group_service.data
    assert result.name == new_item_group.name


def test_update_item_group(item_group_service, mock_db_service):
    item_group_id = 1
    item_group = item_group_service.get_item_group(item_group_id)
    assert mock_db_service.get.call_count == 0
    assert item_group is not None

    updated_item_group = item_group.copy(update={"name": "Updated Type A"})
    mock_db_service.update.return_value = updated_item_group

    result = item_group_service.update_item_group(item_group_id, updated_item_group)

    assert mock_db_service.update.call_count == 1
    assert result.name == "Updated Type A"
    updated_item_group = item_group_service.get_item_group(item_group_id)
    assert updated_item_group.name == "Updated Type A"


def test_update_item_group_archived(item_group_service, mock_db_service):
    item_group_id = 1
    item_group = item_group_service.get_item_group(item_group_id)
    assert mock_db_service.get.call_count == 0
    assert item_group is not None

    mock_db_service.update.return_value = item_group.copy(update={"is_archived": True})

    updateditem_group = item_group_service.archive_item_group(item_group_id)
    assert updateditem_group.is_archived == True
    assert mock_db_service.update.call_count == 1

    updated_item_group = item_group.copy(update={"name": "naame"})

    result = item_group_service.update_item_group(item_group_id, updated_item_group)

    assert mock_db_service.update.call_count == 1
    assert result is None
    updated_item_group = item_group_service.get_item_group(item_group_id)
    assert updated_item_group.is_archived


def test_archive_item_group(item_group_service, mock_db_service):
    item_group_id = 1
    item_group = item_group_service.get_item_group(item_group_id)
    mock_db_service.update.return_value = item_group

    result = item_group_service.archive_item_group(item_group_id)

    assert mock_db_service.update.call_count == 1
    assert result.is_archived
    new_item_group = item_group_service.get_item_group(item_group_id)
    assert new_item_group.is_archived


def test_archive_item_group_not_found(item_group_service, mock_db_service):
    item_group_id = non_existent_id
    result = item_group_service.archive_item_group(item_group_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_item_group(item_group_service, mock_db_service):
    item_group_id = 1
    item_group = item_group_service.get_item_group(item_group_id)
    mock_db_service.update.return_value = item_group

    result = item_group_service.unarchive_item_group(item_group_id)

    assert mock_db_service.update.call_count == 1
    assert not result.is_archived
    new_item_group = item_group_service.get_item_group(item_group_id)
    assert not new_item_group.is_archived


def test_unarchive_item_group_not_found(item_group_service, mock_db_service):
    item_group_id = non_existent_id
    result = item_group_service.unarchive_item_group(item_group_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_item_group_archived(item_group_service):
    assert item_group_service.is_item_group_archived(1) is False
    assert item_group_service.is_item_group_archived(3) is True
    assert item_group_service.is_item_group_archived(99) is None
