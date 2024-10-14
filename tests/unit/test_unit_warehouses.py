import pytest
from api.models.warehouses import Warehouses

test_data = [
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
            "email": "blamore@example.net",
        },
        "created_at": "1983-04-13 04:59:55",
        "updated_at": "2007-02-08 20:11:00",
    },
    {
        "id": 2,
        "code": "JHXPLM22",
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
        "created_at": "1990-07-22 11:15:35",
        "updated_at": "2010-03-18 09:20:45",
    },
    {
        "id": 3,
        "code": "FNDXDK88",
        "name": "Utrecht cargo hub",
        "address": "Maliebaan 49",
        "zip": "3581 CD",
        "city": "Utrecht",
        "province": "Utrecht",
        "country": "NL",
        "contact": {
            "name": "Johan van Dijk",
            "phone": "(030) 2302300",
            "email": "jvandijk@example.org",
        },
        "created_at": "2002-11-05 13:34:22",
        "updated_at": "2015-06-27 14:12:58",
    },
    {
        "id": 4,
        "code": "ZHYDPS19",
        "name": "Rotterdam port hub",
        "address": "Waalhaven 20",
        "zip": "3088 KA",
        "city": "Rotterdam",
        "province": "Zuid-Holland",
        "country": "NL",
        "contact": {
            "name": "Petra Jansen",
            "phone": "(010) 4782009",
            "email": "pjansen@example.com",
        },
        "created_at": "1995-03-12 08:45:12",
        "updated_at": "2018-12-05 10:55:42",
    },
    {
        "id": 5,
        "code": "DKQLWB91",
        "name": "Amsterdam cargo hub",
        "address": "Schiphol Boulevard 123",
        "zip": "1118 BG",
        "city": "Amsterdam",
        "province": "Noord-Holland",
        "country": "NL",
        "contact": {
            "name": "Mark de Vries",
            "phone": "(020) 6549871",
            "email": "mdevries@example.net",
        },
        "created_at": "2005-05-15 17:32:44",
        "updated_at": "2020-08-12 12:43:30",
    },
]

new_data = {
    "id": 6,
    "code": "KLU87413M",
    "name": "Den Haag cargo hub",
    "address": "Stationsweg 45",
    "zip": "2516 AA",
    "city": "Den Haag",
    "province": "Zuid-Holland",
    "country": "NL",
    "contact": {
        "name": "Linda Bakker",
        "phone": "(070) 1234567",
        "email": "lbakker@example.com",
    },
    "created_at": "2022-01-14 16:04:12",
    "updated_at": "2024-02-18 22:41:38",
}


@pytest.fixture
def warehouses_instance():
    warehouses = Warehouses(root_path="", is_debug=True)

    for data in test_data:
        warehouses.add_warehouse(data)
    return warehouses


def test_get_warehouses(warehouses_instance):
    warehouses = warehouses_instance.get_warehouses()
    assert len(warehouses) == len(test_data)
    assert warehouses[0]["code"] == "YQZZNL56"


def test_get_warehouse(warehouses_instance):
    warehouse = warehouses_instance.get_warehouse(test_data[0]["id"])
    assert warehouse is not None
    assert warehouse["code"] == "YQZZNL56"
    assert warehouse["name"] == "Heemskerk cargo hub"


def test_get_nonexistent_warehouse(warehouses_instance):
    warehouse = warehouses_instance.get_warehouse(9999)
    assert warehouse is None


def test_add_warehouse(warehouses_instance):
    current_length = len(warehouses_instance.get_warehouses())
    warehouses_instance.add_warehouse(new_data)
    assert len(warehouses_instance.get_warehouses()) == current_length + 1
    added_warehouse = warehouses_instance.get_warehouse(new_data["id"])
    assert added_warehouse is not None
    assert added_warehouse["id"] == new_data["id"]
    assert added_warehouse["code"] == new_data["code"]
    assert "created_at" in added_warehouse
    assert "updated_at" in added_warehouse


def test_update_warehouse(warehouses_instance):
    updated_warehouse = test_data[0].copy()
    updated_warehouse["code"] = "UPDATED123"
    updated_warehouse["name"] = "Updated Heemskerk cargo hub"
    warehouses_instance.update_warehouse(updated_warehouse["id"], updated_warehouse)

    warehouse = warehouses_instance.get_warehouse(updated_warehouse["id"])
    assert warehouse is not None
    assert warehouse["code"] == "UPDATED123"
    assert warehouse["name"] == "Updated Heemskerk cargo hub"
    assert "updated_at" in warehouse


def test_remove_warehouse(warehouses_instance):
    warehouses_instance.add_warehouse(new_data)
    current_length = len(warehouses_instance.get_warehouses())
    warehouses_instance.remove_warehouse(new_data["id"])
    assert len(warehouses_instance.get_warehouses()) == current_length - 1
    removed_warehouse = warehouses_instance.get_warehouse(new_data["id"])
    assert removed_warehouse is None


def test_update_nonexistent_warehouse(warehouses_instance):
    non_existent_warehouse = {
        "id": 9999,
        "code": "NONEXIST",
        "name": "Nonexistent Warehouse",
        "address": "Nowhere Street",
        "zip": "0000 ZZ",
        "city": "Nowhere",
        "province": "Nowhere",
        "country": "NL",
        "contact": {
            "name": "Ghost User",
            "phone": "(000) 0000000",
            "email": "ghost@example.com",
        },
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00",
    }
    warehouses_instance.update_warehouse(
        non_existent_warehouse["id"], non_existent_warehouse
    )
    warehouse = warehouses_instance.get_warehouse(non_existent_warehouse["id"])
    assert warehouse is None


def test_remove_nonexistent_warehouse(warehouses_instance):
    current_length = len(warehouses_instance.get_warehouses())
    warehouses_instance.remove_warehouse(9999)
    assert len(warehouses_instance.get_warehouses()) == current_length
