import pytest
from app.models.items import Items

test_data = [
    {
        "uid": "P000000",
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
        "updated_at": "2008-09-02 20:34:48",
    },
    {
        "uid": "P000001",
        "code": "TRF58743D",
        "description": "Proactive empowering methodology",
        "short_description": "synergy",
        "upc_code": "7489813941287",
        "model_number": "XL-672301-cZD",
        "commodity_code": "vsy810",
        "item_line": 47,
        "item_group": 38,
        "item_type": 29,
        "unit_purchase_quantity": 15,
        "unit_order_quantity": 22,
        "pack_order_quantity": 19,
        "supplier_id": 11,
        "supplier_code": "SUP318",
        "supplier_part_number": "uQx-57z8",
        "created_at": "2011-05-25 12:14:29",
        "updated_at": "2019-07-30 16:20:54",
    },
    {
        "uid": "P000002",
        "code": "HIK32984T",
        "description": "Innovative leading-edge project",
        "short_description": "solution",
        "upc_code": "1347102850643",
        "model_number": "LT-584736-mJK",
        "commodity_code": "pzi456",
        "item_line": 58,
        "item_group": 19,
        "item_type": 42,
        "unit_purchase_quantity": 27,
        "unit_order_quantity": 39,
        "pack_order_quantity": 12,
        "supplier_id": 78,
        "supplier_code": "SUP957",
        "supplier_part_number": "oFp-33r5",
        "created_at": "2019-03-14 09:37:45",
        "updated_at": "2023-10-05 21:50:13",
    },
    {
        "uid": "P000003",
        "code": "PZX65421B",
        "description": "Team-oriented holistic framework",
        "short_description": "dynamic",
        "upc_code": "5701483942235",
        "model_number": "GH-904234-sXP",
        "commodity_code": "kuf623",
        "item_line": 81,
        "item_group": 29,
        "item_type": 7,
        "unit_purchase_quantity": 18,
        "unit_order_quantity": 10,
        "pack_order_quantity": 31,
        "supplier_id": 5,
        "supplier_code": "SUP662",
        "supplier_part_number": "mPq-14d9",
        "created_at": "2016-08-02 07:45:19",
        "updated_at": "2021-12-11 13:22:41",
    },
]

new_item = {
    "uid": "P000004",
    "code": "KLU87413M",
    "description": "Synergistic strategic partnership",
    "short_description": "integration",
    "upc_code": "1458279305768",
    "model_number": "UV-953190-yFQ",
    "commodity_code": "hwt238",
    "item_line": 63,
    "item_group": 84,
    "item_type": 31,
    "unit_purchase_quantity": 33,
    "unit_order_quantity": 17,
    "pack_order_quantity": 28,
    "supplier_id": 44,
    "supplier_code": "SUP214",
    "supplier_part_number": "hLm-95a3",
    "created_at": "2022-01-14 16:04:12",
    "updated_at": "2024-02-18 22:41:38",
}


@pytest.fixture
def items_instance():
    return Items("", is_debug=True, items=test_data)


def test_get_items(items_instance):
    items = items_instance.get_items()
    assert len(items) == len(test_data)
    assert items[0]["code"] == "SGK13406K"
    assert True == False


def test_get_item(items_instance):
    item = items_instance.get_item(test_data[0]["uid"])
    assert item["code"] == "SGK13406K"


def test_get_nonexistent_item(items_instance):
    item = items_instance.get_item("DitIsEenIdDieTochNooitBestaat")
    assert item is None


def test_add_item(items_instance):
    current_length = len(items_instance.data)
    items_instance.add_item(new_item)
    assert len(items_instance.data) == current_length + 1
    added_item = items_instance.get_item(new_item["uid"])
    assert added_item["uid"] == new_item["uid"]
    assert "created_at" in added_item
    assert "updated_at" in added_item


def test_update_item(items_instance):
    updated_item = test_data[0]
    updated_item["code"] = "UpdatedCode"
    updated_item["short_description"] = "UpdatedShortDescription"
    items_instance.update_item(updated_item["uid"], updated_item)
    assert items_instance.data[0]["code"] == "UpdatedCode"
    assert "updated_at" in items_instance.get_item(updated_item["uid"])


def test_remove_item(items_instance):
    current_length = len(items_instance.data)
    items_instance.remove_item(new_item["uid"])
    assert len(items_instance.data) == current_length - 1


def test_get_items_for_item_line(items_instance):
    items = items_instance.get_items_for_item_line(test_data[1]["item_line"])
    assert len(items) == 1
    assert items[0]["uid"] == test_data[1]["uid"]


def test_get_items_for_item_group(items_instance):
    items = items_instance.get_items_for_item_group(test_data[2]["item_group"])
    assert len(items) == 1
    assert items[0]["uid"] == test_data[2]["uid"]


def test_get_items_for_item_type(items_instance):
    items = items_instance.get_items_for_item_type(test_data[0]["item_type"])
    assert len(items) == 1
    assert items[0]["uid"] == test_data[0]["uid"]


def test_get_items_for_supplier(items_instance):
    items = items_instance.get_items_for_supplier(test_data[1]["supplier_id"])
    assert len(items) == 1
    assert items[0]["uid"] == test_data[1]["uid"]
