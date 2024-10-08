import json
import pytest
from unittest.mock import patch, mock_open
from models.items import Items


@pytest.fixture
def items_instance():
    """Fixture to create an instance of Items."""
    return Items("test_path/", is_debug=True)


def test_load_items(items_instance):
    mock_data = '''[
        {
            "uid": "P000020",
            "code": "SGK13406K",
            "description": "Customer-focused cohesive task-force",
            "short_description": "operation",
            "upc_code": "1210292288171",
            "model_number": "HP-957193-eHN",
            "commodity_code": "nxa480",
            "item_line": 36,
            "item_group": 59,
            "item_type": 16,
            "unit_purchase_quantity": 8,
            "unit_order_quantity": 14,
            "pack_order_quantity": 23,
            "supplier_id": 53,
            "supplier_code": "SUP585",
            "supplier_part_number": "rTh-24u2",
            "created_at": "2000-10-18 20:31:38",
            "updated_at": "2008-09-02 20:34:48"
        }
    ]'''
    
    with patch('builtins.open', mock_open(read_data=mock_data)):
        items_instance.load(is_debug=False)
        assert len(items_instance.data) == 1
        assert items_instance.data[0]['uid'] == 'P000020'
        assert items_instance.data[0]['code'] == 'SGK13406K'


def test_get_items(items_instance):
    items_instance.data = [{
        "uid": "P000020",
        "code": "SGK13406K"
    }]
    items = items_instance.get_items()
    assert len(items) == 1
    assert items[0]['code'] == 'SGK13406K'


def test_get_item(items_instance):
    items_instance.data = [{
        "uid": "P000020",
        "code": "SGK13406K"
    }]
    item = items_instance.get_item("P000020")
    assert item['code'] == 'SGK13406K'
    
    item = items_instance.get_item("P000021")
    assert item is None


def test_add_item(items_instance):
    items_instance.data = []
    new_item = {
        "uid": "P000021",
        "code": "SGK13407K",
        "description": "Another test item"
    }
    items_instance.add_item(new_item)
    assert len(items_instance.data) == 1
    assert items_instance.data[0]['uid'] == 'P000021'
    assert 'created_at' in items_instance.data[0]
    assert 'updated_at' in items_instance.data[0]


def test_update_item(items_instance):
    items_instance.data = [{
        "uid": "P000020",
        "code": "SGK13406K"
    }]
    updated_item = {
        "uid": "P000020",
        "code": "UpdatedCode"
    }
    items_instance.update_item("P000020", updated_item)
    assert items_instance.data[0]['code'] == 'UpdatedCode'
    assert 'updated_at' in items_instance.data[0]


def test_remove_item(items_instance):
    items_instance.data = [{
        "uid": "P000020",
        "code": "SGK13406K"
    }]
    items_instance.remove_item("P000020")
    assert len(items_instance.data) == 0


def test_get_items_for_item_line(items_instance):
    items_instance.data = [
        {"uid": "P000020", "item_line": 36, "code": "Item Line 1"},
        {"uid": "P000021", "item_line": 35, "code": "Item Line 2"}
    ]
    items = items_instance.get_items_for_item_line(35)
    assert len(items) == 1
    assert items[0]['uid'] == 'P000021'


def test_get_items_for_item_group(items_instance):
    items_instance.data = [
        {"uid": "P000020", "item_group": 59, "code": "Group Item 1"},
        {"uid": "P000021", "item_group": 58, "code": "Group Item 2"}
    ]
    items = items_instance.get_items_for_item_group(58)
    assert len(items) == 1
    assert items[0]['uid'] == 'P000021'


def test_get_items_for_item_type(items_instance):
    items_instance.data = [
        {"uid": "P000020", "item_type": 16, "code": "Type Item 1"},
        {"uid": "P000021", "item_type": 15, "code": "Type Item 2"}
    ]
    items = items_instance.get_items_for_item_type(15)
    assert len(items) == 1
    assert items[0]['uid'] == 'P000021'


def test_get_items_for_supplier(items_instance):
    items_instance.data = [
        {"uid": "P000020", "supplier_id": 53, "code": "Supplier Item 1"},
        {"uid": "P000021", "supplier_id": 52, "code": "Supplier Item 2"}
    ]
    items = items_instance.get_items_for_supplier(52)
    assert len(items) == 1
    assert items[0]['uid'] == 'P000021'