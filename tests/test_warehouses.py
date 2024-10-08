import json
import pytest
from unittest.mock import patch, mock_open
from api.models.warehouses import Warehouses


@pytest.fixture
def warehouses_instance():
    """Fixture to create an instance of Warehouses."""
    return Warehouses("test_path/", is_debug=True)


def test_load_warehouses(warehouses_instance):
    mock_data = """[
        {
            "id": 1,
            "code": "YQZZNL56",
            "name": "Heemskerk cargo hub",
            "address": "Karlijndreef 281",
            "zip": "4002 AS",
            "city": "Heemskerk",
            "province": "Friesland",
            "country": "NL",
            "contact": {
                "name": "Fem Keijzer",
                "phone": "(078) 0013363",
                "email": "blamore@example.net"
            },
            "created_at": "1983-04-13 04:59:55",
            "updated_at": "2007-02-08 20:11:00"
        }
    ]"""

    with patch("builtins.open", mock_open(read_data=mock_data)):
        warehouses_instance.load(is_debug=False)
        assert len(warehouses_instance.data) == 1
        assert warehouses_instance.data[0]["id"] == 1
        assert warehouses_instance.data[0]["name"] == "Heemskerk cargo hub"


def test_get_warehouses(warehouses_instance):
    warehouses_instance.data = [{"id": "1", "name": "Heemskerk cargo hub"}]
    warehouses = warehouses_instance.get_warehouses()
    assert len(warehouses) == 1
    assert warehouses[0]["name"] == "Heemskerk cargo hub"


def test_get_warehouse(warehouses_instance):
    warehouses_instance.data = [{"id": "1", "name": "Heemskerk cargo hub"}]
    warehouse = warehouses_instance.get_warehouse("1")
    assert warehouse["name"] == "Heemskerk cargo hub"


def test_add_warehouse(warehouses_instance):
    warehouse = {
        "id": "2",
        "name": "Heemskerk cargo hub 2",
        "address": "Karlijndreef 281b",
        "zip": "4002 AS",
        "city": "Heemskerk",
        "province": "Friesland",
        "country": "NL",
        "contact": {
            "name": "Fem Keijzer",
            "phone": "(078) 0013363",
            "email": "blamore@example.net",
        },
        "created_at": "",
        "updated_at": "",
    }

    warehouses_instance.add_warehouse(warehouse)
    assert len(warehouses_instance.data) == 1
    assert warehouses_instance.data[0]["name"] == "Heemskerk cargo hub 2"
    assert warehouses_instance.data[0]["id"] == "2"
    assert warehouses_instance.data[0]["created_at"] != ""
    assert warehouses_instance.data[0]["updated_at"] != ""


def test_update_warehouse(warehouses_instance):
    warehouse = {
        "id": "2",
        "name": "Heemskerk cargo hub 2",
        "address": "Karlijndreef 281b",
        "zip": "4002 AS",
        "city": "Heemskerk",
        "province": "Friesland",
        "country": "NL",
        "contact": {
            "name": "Fem Keijzer",
            "phone": "(078) 0013363",
            "email": "blamore@example.net",
        },
        "created_at": "",
        "updated_at": "",
    }

    warehouses_instance.data = [warehouse]
    warehouse["name"] = "Heemskerk cargo hub 3"
    warehouses_instance.update_warehouse("2", warehouse)
    assert len(warehouses_instance.data) == 1
    assert warehouses_instance.data[0]["name"] == "Heemskerk cargo hub 3"
    assert warehouses_instance.data[0]["id"] == "2"
    assert warehouses_instance.data[0]["created_at"] == ""
    assert warehouses_instance.data[0]["updated_at"] != ""


def test_remove_warehouse(warehouses_instance):
    warehouse = {
        "id": "2",
        "name": "Heemskerk cargo hub 2",
        "address": "Karlijndreef 281b",
        "zip": "4002 AS",
        "city": "Heemskerk",
        "province": "Friesland",
        "country": "NL",
        "contact": {
            "name": "Fem Keijzer",
            "phone": "(078) 0013363",
            "email": "blamore@example.net",
        },
        "created_at": "",
        "updated_at": "",
    }

    warehouses_instance.data = [warehouse]
    warehouses_instance.remove_warehouse("2")
    assert len(warehouses_instance.data) == 0
    assert warehouses_instance.data == []
