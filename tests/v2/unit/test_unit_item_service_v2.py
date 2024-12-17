from unittest.mock import Mock
import pytest
from app.models.v2.item import Item
from app.services.v2.model_services.item_services import ItemService


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def item_service(mock_db_service):
    """Fixture to create an ItemService instance with the mocked DatabaseService."""
    service = ItemService(
        True,
        [
            Item(
                uid="P000001",
                code="sjQ23408K",
                description="Face-to-face clear-thinking complexity",
                short_description="must",
                upc_code="6523540947122",
                model_number="63-OFFTq0T",
                commodity_code="oTo304",
                item_line=11,
                item_group=73,
                item_type=14,
                unit_purchase_quantity=47,
                unit_order_quantity=13,
                pack_order_quantity=11,
                supplier_id=34,
                supplier_code="SUP423",
                supplier_part_number="E-86805-uTM",
                created_at="2015-02-19 16:08:24",
                updated_at="2015-09-26 06:37:56",
            ),
            Item(
                uid="P000002",
                code="nyg48736S",
                description="Focused transitional alliance",
                short_description="may",
                upc_code="9733132830047",
                model_number="ck-109684-VFb",
                commodity_code="y-20588-owy",
                item_line=69,
                item_group=85,
                item_type=39,
                unit_purchase_quantity=10,
                unit_order_quantity=15,
                pack_order_quantity=23,
                supplier_id=57,
                supplier_code="SUP312",
                supplier_part_number="j-10730-ESk",
                created_at="2020-05-31 16:00:08",
                updated_at="2020-11-08 12:49:21",
            ),
            Item(
                uid="P000003",
                code="QVm03739H",
                description="Cloned actuating artificial intelligence",
                short_description="we",
                upc_code="3722576017240",
                model_number="aHx-68Q4",
                commodity_code="t-541-F0g",
                item_line=54,
                item_group=88,
                item_type=42,
                unit_purchase_quantity=30,
                unit_order_quantity=17,
                pack_order_quantity=11,
                supplier_id=2,
                supplier_code="SUP237",
                supplier_part_number="r-920-z2C",
                created_at="1994-06-02 06:38:40",
                updated_at="1999-10-13 01:10:32",
            ),
        ],
        mock_db_service,
    )
    return service


def test_get_all_items(item_service, mock_db_service):
    mock_db_service.get_all.return_value = item_service.data
    items = item_service.get_all_items()

    assert len(items) == len(item_service.data)
    assert items[0].uid == "P000001"
    assert mock_db_service.get_all.call_count == 1


def test_get_items(item_service, mock_db_service):
    items = item_service.get_items()

    assert len(items) == len(item_service.data)
    assert items[0].uid == "P000001"
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_supplier(item_service, mock_db_service):
    supplier_id = 34
    items = item_service.get_items_for_supplier(supplier_id)

    assert len(items) == 1
    assert items[0].supplier_id == supplier_id
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_supplier_not_found(item_service, mock_db_service):
    supplier_id = 100
    items = item_service.get_items_for_supplier(supplier_id)

    assert len(items) == 0
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_group(item_service, mock_db_service):
    item_group = 73
    items = item_service.get_items_for_item_group(item_group)

    assert len(items) == 1
    assert items[0].item_group == item_group
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_group_not_found(item_service, mock_db_service):
    item_group = 100
    items = item_service.get_items_for_item_group(item_group)

    assert len(items) == 0
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_line(item_service, mock_db_service):
    item_line = 11
    items = item_service.get_items_for_item_line(item_line)

    assert len(items) == 1
    assert items[0].item_line == item_line
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_line_not_found(item_service, mock_db_service):
    item_line = 100
    items = item_service.get_items_for_item_line(item_line)

    assert len(items) == 0
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_type(item_service, mock_db_service):
    item_type = 14
    items = item_service.get_items_for_item_type(item_type)

    assert len(items) == 1
    assert items[0].item_type == item_type
    assert mock_db_service.get_all.call_count == 0


def test_get_items_for_item_type_not_found(item_service, mock_db_service):
    item_type = 100
    items = item_service.get_items_for_item_type(item_type)

    assert len(items) == 0
    assert mock_db_service.get_all.call_count == 0


def test_get_item(item_service, mock_db_service):
    item_id = "P000001"
    item = item_service.get_item(item_id)

    assert item.uid == item_id
    assert mock_db_service.get.call_count == 0


def test_get_item_not_found(item_service, mock_db_service):
    item_id = "P000004"
    mock_db_service.get.return_value = None
    item = item_service.get_item(item_id)

    assert item is None
    assert mock_db_service.get.call_count == 1


def test_add_item(item_service, mock_db_service):
    new_uid = item_service.generate_uid()
    new_item = Item(
        code="QVm03739H",
        description="Cloned actuating artificial intelligence",
        short_description="we",
        upc_code="3722576017240",
        model_number="aHx-68Q4",
        commodity_code="t-541-F0g",
        item_line=54,
        item_group=88,
        item_type=42,
        unit_purchase_quantity=30,
        unit_order_quantity=17,
        pack_order_quantity=11,
        supplier_id=2,
        supplier_code="SUP237",
        supplier_part_number="r-920-z2C",
        created_at="1994-06-02 06:38:40",
        updated_at="1999-10-13 01:10:32",
    )

    mock_db_service.insert.return_value = new_item

    result = item_service.add_item(new_item)

    assert mock_db_service.insert.call_count == 1
    assert new_uid == new_item.uid
    assert item_service.get_item(result.uid).description == new_item.description
    assert result == new_item


def test_update_item(item_service, mock_db_service):
    item_id = "P000001"
    updated_item = Item(
        uid="P000001",
        code="sjQ23408K",
        description="Face-to-face clear-thinking complexity1111111111111",
        short_description="must2",
        upc_code="6523540947122",
        model_number="63-OFFTq0T",
        commodity_code="oTo304",
        item_line=11,
        item_group=73,
        item_type=14,
        unit_purchase_quantity=47,
        unit_order_quantity=13,
        pack_order_quantity=11,
        supplier_id=34,
        supplier_code="SUP423",
        supplier_part_number="E-86805-uTM",
        created_at="2015-02-19 16:08:24",
        updated_at="2015-09-26 06:37:56",
    )

    mock_db_service.update.return_value = updated_item

    result = item_service.update_item(item_id, updated_item)

    assert mock_db_service.update.call_count == 1
    assert (
        item_service.get_item(updated_item.uid).description == updated_item.description
    )
    assert result == updated_item


def test_update_item_not_found(item_service, mock_db_service):
    item_id = "P000004"
    updated_item = Item(
        uid="P000004",
        code="sjQ23408K",
        description="Face-to-face clear-thinking complexity1111111111111",
        short_description="must2",
        upc_code="6523540947122",
        model_number="63-OFFTq0T",
        commodity_code="oTo304",
        item_line=11,
        item_group=73,
        item_type=14,
        unit_purchase_quantity=47,
        unit_order_quantity=13,
        pack_order_quantity=11,
        supplier_id=34,
        supplier_code="SUP423",
        supplier_part_number="E-86805-uTM",
        created_at="2015-02-19 16:08:24",
        updated_at="2015-09-26 06:37:56",
    )
    mock_db_service.get.return_value = None
    result = item_service.update_item(item_id, updated_item)

    assert mock_db_service.update.call_count == 0
    assert mock_db_service.get.call_count == 1
    assert result is None


def test_has_item_archived_entities(item_service, mock_db_service):
    item_id = "P000001"
    item = item_service.get_item(item_id)

    result = item_service.has_item_archived_entities(item)

    assert result == False


def test_archive_item(item_service, mock_db_service):
    item_id = "P000001"
    item = item_service.get_item(item_id)
    mock_db_service.update.return_value = item

    result = item_service.archive_item(item_id)

    assert mock_db_service.update.call_count == 1
    found_item = item_service.get_item(item_id)
    assert found_item is not None
    assert found_item.is_archived == True
    assert result == item


def test_archive_item_not_found(item_service, mock_db_service):
    item_id = "P000004"
    result = item_service.archive_item(item_id)

    assert mock_db_service.update.call_count == 0
    assert result is None


def test_is_item_archived(item_service, mock_db_service):
    item_id = "P000001"
    item = item_service.get_item(item_id)

    result = item_service.is_item_archived(item_id)

    assert mock_db_service.get.call_count == 0
    assert result == item.is_archived


def test_is_item_archived_not_found(item_service, mock_db_service):
    item_id = "P000004"
    result = item_service.is_item_archived(item_id)

    assert mock_db_service.get.call_count == 0
    assert result is None


def test_get_all_unarchived_items(item_service, mock_db_service):
    item_id = "P000001"
    item_service.archive_item(item_id)
    items = item_service.get_items()

    assert len(items) == 2
    assert items[0].uid != "P000001"
    assert mock_db_service.get_all.call_count == 0


def test_unarchive_item(item_service, mock_db_service):
    item_id = "P000001"
    item = item_service.get_item(item_id)
    mock_db_service.update.return_value = item

    result = item_service.unarchive_item(item_id)

    assert mock_db_service.update.call_count == 1
    found_item = item_service.get_item(item_id)
    assert found_item is not None
    assert found_item.is_archived == False
    assert result == item


def test_unarchive_item_not_found(item_service, mock_db_service):
    item_id = "P000004"
    result = item_service.unarchive_item(item_id)

    assert mock_db_service.update.call_count == 0
    assert result is None


def test_generate_uid(item_service):
    generate_uid = item_service.generate_uid()
    assert isinstance(generate_uid, str)
    assert generate_uid[-1].isdigit()
    assert generate_uid[0] == "P"
    assert generate_uid[-1] == f"{len(item_service.data) + 1}"


def test_generate_uid_empty(item_service):
    item_service.data = []
    generate_uid = item_service.generate_uid()
    assert isinstance(generate_uid, str)
    assert generate_uid[-1].isdigit()
    assert generate_uid[0] == "P"
    assert generate_uid[-1] == "1"


def test_generate_uid_single_item(item_service):
    item_service.data = [item_service.data[0]]
    generate_uid = item_service.generate_uid()
    assert isinstance(generate_uid, str)
    assert generate_uid[-1].isdigit()
    assert generate_uid[0] == "P"
    assert generate_uid[-1] == "2"


def test_generate_uid_many_items(item_service):
    all_items = []
    for i in range(1, 99998):
        test_item_to_add = item_service.data[0].copy()
        test_item_to_add.uid = f"p{i:06d}"
        all_items.append(test_item_to_add)
    item_service.data = all_items
    generate_uid = item_service.generate_uid()
    assert isinstance(generate_uid, str)
    assert generate_uid[0] == "P"
    assert generate_uid[1:] == "099998"
