import json
import pytest
from unittest.mock import patch, mock_open
from api.models.orders import Orders


@pytest.fixture
def orders_instance():
    """Fixture to create an instance of Orders."""
    return Orders("test_path/", is_debug=True)

def test_load_orders(orders_instance):
    mock_data = '''[
        {
            "id": 1,
            "source_id": 3,
            "order_date": "2024-06-16T09:12:10Z",
            "request_date": "2024-06-20T09:12:10Z",
            "reference": "ORD00001",
            "reference_extra": "Benzine fit schreeuwen.",
            "order_status": "Packed",
            "notes": "Kosten wind voorbeeld winnen poes winter perfect.",
            "shipping_notes": "Kans fruit snelheid tennis bijten vliegtuig rijk.",
            "picking_notes": "Bank springen aanraken spreken moeder scherp gif.",
            "warehouse_id": 25,
            "ship_to": 9291,
            "bill_to": 9291,
            "shipment_id": null,
            "total_amount": 6831.19,
            "total_discount": 411.76,
            "total_tax": 937.76,
            "total_surcharge": 92.01,
            "created_at": "2024-06-16T09:12:10Z",
            "updated_at": "2024-06-18T05:12:10Z",
            "items": [
                {
                    "item_id": "P006383",
                    "amount": 32
                }
            ]
        }
    ]'''
    
    with patch('builtins.open', mock_open(read_data=mock_data)):
        orders_instance.load(is_debug=False)
        assert len(orders_instance.data) == 1
        assert orders_instance.data[0]['id'] == 1
        assert orders_instance.data[0]['reference'] == 'ORD00001'



def test_get_orders(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "reference": "ORD00001"
    }]
    orders = orders_instance.get_orders()
    assert len(orders) == 1
    assert orders[0]['reference'] == 'ORD00001'


def test_get_order(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "reference": "ORD00001"
    }]
    order = orders_instance.get_order(1)
    assert order['reference'] == 'ORD00001'
    
    order = orders_instance.get_order(2)
    assert order is None


def test_get_items_in_order(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "reference": "ORD00001",
        "items": [{"item_id": "P000001", "amount": 10}]
    }]
    items = orders_instance.get_items_in_order(1)
    assert len(items) == 1
    assert items[0]["item_id"] == "P000001"
    assert items[0]["amount"] == 10
    
    items = orders_instance.get_items_in_order(2)
    assert items is None


def test_get_orders_in_shipment(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "shipment_id": 123,
        "reference": "ORD00001"
    }, {
        "id": 2,
        "shipment_id": 456,
        "reference": "ORD00002"
    }]
    
    orders_in_shipment = orders_instance.get_orders_in_shipment(123)
    assert len(orders_in_shipment) == 1
    assert orders_in_shipment[0] == 1

    orders_in_shipment = orders_instance.get_orders_in_shipment(789)
    assert len(orders_in_shipment) == 0


def test_get_orders_for_client(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "ship_to": 100,
        "bill_to": 101,
        "reference": "ORD00001"
    }, {
        "id": 2,
        "ship_to": 102,
        "bill_to": 103,
        "reference": "ORD00002"
    }]
    
    orders_for_client = orders_instance.get_orders_for_client(100)
    assert len(orders_for_client) == 1
    assert orders_for_client[0]["reference"] == "ORD00001"
    
    orders_for_client = orders_instance.get_orders_for_client(103)
    assert len(orders_for_client) == 1
    assert orders_for_client[0]["reference"] == "ORD00002"
    
    orders_for_client = orders_instance.get_orders_for_client(999)
    assert len(orders_for_client) == 0


def test_add_order(orders_instance):
    orders_instance.data = []
    new_order = {
        "id": "2",
        "reference": "ORD00002",
        "notes": "Another test order"
    }
    orders_instance.add_order(new_order)
    assert len(orders_instance.data) == 1
    assert orders_instance.data[0]['reference'] == 'ORD00002'
    assert 'created_at' in orders_instance.data[0]
    assert 'updated_at' in orders_instance.data[0]


def test_update_order(orders_instance):
    orders_instance.data = [{
        "id": 2,
        "reference": "ORD00002",
        "notes": "Another test order"
    }]
    updated_order = {
        "id": 2,
        "reference": "ORD00002",
        "notes": "Another updated test order"
    }
    orders_instance.update_order(2, updated_order)
    assert orders_instance.data[0]['notes'] == 'Another updated test order'
    assert 'updated_at' in orders_instance.data[0]
    print(orders_instance.data[0])


def test_update_orders_in_shipment(orders_instance):
    orders_instance.data = [{
        "id": 1,
        "shipment_id": 123,
        "reference": "ORD00001",
        "order_status": "Packed"
    }, {
        "id": 2,
        "shipment_id": 456,
        "reference": "ORD00002",
        "order_status": "Scheduled"
    }]
    
    orders_instance.update_orders_in_shipment(123, [1])
    
    assert orders_instance.data[0]["shipment_id"] == 123
    assert orders_instance.data[0]["order_status"] == "Packed"
    assert orders_instance.data[1]["shipment_id"] == 456
    assert orders_instance.data[1]["order_status"] == "Scheduled"


def test_remove_order(orders_instance):
    orders_instance.data = [{
        "id": 3,
        "reference": "ORD00003",
        "notes": "Just another test order"
    }]

    orders_instance.remove_order(3)
    assert len(orders_instance.data) == 0
    