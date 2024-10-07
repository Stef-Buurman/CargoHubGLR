import json
import pytest
from unittest.mock import patch, mock_open
from models.items import Items  # Replace 'your_module' with the actual module name


@pytest.fixture
def items_instance():
    """Fixture to create an instance of Items."""
    return Items("test_path/", is_debug=True)


def test_load_items(items_instance):
    mock_data = '[{"id": 1, "name": "Test Item"}]'
    
    with patch('builtins.open', mock_open(read_data=mock_data)):
        items_instance.load(is_debug=False)
        assert len(items_instance.data) == 1
        assert items_instance.data[0]['name'] == 'Test Item'


def test_get_items(items_instance):
    items_instance.data = [{"id": 1, "name": "Test Item"}]
    items = items_instance.get_items()
    assert len(items) == 1
    assert items[0]['name'] == 'Test Item'


def test_get_item(items_instance):
    items_instance.data = [{"id": 1, "name": "Test Item"}]
    item = items_instance.get_item(1)
    assert item['name'] == 'Test Item'
    
    item = items_instance.get_item(2)
    assert item is None


def test_add_item(items_instance):
    items_instance.data = []
    new_item = {"id": 2, "name": "New Item"}
    items_instance.add_item(new_item)
    assert len(items_instance.data) == 1
    assert items_instance.data[0]['name'] == 'New Item'
    assert 'created_at' in items_instance.data[0]
    assert 'updated_at' in items_instance.data[0]


def test_update_item(items_instance):
    items_instance.data = [{"id": 1, "name": "Old Item"}]
    updated_item = {"id": 1, "name": "Updated Item"}
    items_instance.update_item(1, updated_item)
    assert items_instance.data[0]['name'] == 'Updated Item'
    assert 'updated_at' in items_instance.data[0]


def test_remove_item(items_instance):
    items_instance.data = [{"id": 1, "name": "Test Item"}]
    items_instance.remove_item(1)
    assert len(items_instance.data) == 0


def test_get_items_for_item_line(items_instance):
    items_instance.data = [
        {"id": 1, "item_line": 2, "name": "Item Line 1"},
        {"id": 2, "item_line": 1, "name": "Item Line 2"}
    ]
    items = items_instance.get_items_for_item_line(1)
    assert len(items) == 1
    assert items[0]['id'] == 2


def test_get_items_for_item_group(items_instance):
    items_instance.data = [
        {"id": 1, "item_group": 2, "name": "Group Item 1"},
        {"id": 2, "item_group": 1, "name": "Group Item 2"}
    ]
    items = items_instance.get_items_for_item_group(1)
    assert len(items) == 1
    assert items[0]['id'] == 2


def test_get_items_for_item_type(items_instance):
    items_instance.data = [
        {"id": 1, "item_type": 2, "name": "Type Item 1"},
        {"id": 2, "item_type": 1, "name": "Type Item 2"}
    ]
    items = items_instance.get_items_for_item_type(1)
    assert len(items) == 1
    assert items[0]['id'] == 2


def test_get_items_for_supplier(items_instance):
    items_instance.data = [
        {"id": 1, "supplier_id": 2, "name": "Supplier Item 1"},
        {"id": 2, "supplier_id": 1, "name": "Supplier Item 2"}
    ]
    items = items_instance.get_items_for_supplier(1)
    assert len(items) == 1
    assert items[0]['id'] == 2
