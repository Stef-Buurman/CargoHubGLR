# import json
# import pytest
# from unittest.mock import patch, mock_open
# from api.models.shipments import Shipments

# @pytest.fixture
# def shipments_instance():
#     """Fixture to create an instance of Shipments."""
#     return Shipments("test_path/", is_debug=True)

# def test_load_shipments(shipments_instance):
#     mock_data = '[{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]'
    
#     with patch('builtins.open', mock_open(read_data=mock_data)):
#         shipments_instance.load(is_debug=False)
#         assert len(shipments_instance.data) == 1
#         assert shipments_instance.data[0]['id'] == 1

# def test_get_shipments(shipments_instance):
#     shipments_instance.data = [{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]
#     shipments = shipments_instance.get_shipments()
#     assert len(shipments) == 1
#     assert shipments[0]['id'] == 1

# def test_get_shipment(shipments_instance):
#     shipments_instance.data = [{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]
#     shipment = shipments_instance.get_shipment(1)
#     assert shipment['id'] == 1
    
#     shipment = shipments_instance.get_shipment(2)
#     assert shipment is None

# def test_add_shipment(shipments_instance):
#     shipments_instance.data = []
#     new_shipment = {"id": 2, "items": [{"item_id": 1, "amount": 5}]}
#     shipments_instance.add_shipment(new_shipment)
#     assert len(shipments_instance.data) == 1
#     assert shipments_instance.data[0]['id'] == 2
#     assert 'created_at' in shipments_instance.data[0]
#     assert 'updated_at' in shipments_instance.data[0]

# def test_update_shipment(shipments_instance):
#     shipments_instance.data = [{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]
#     updated_shipment = {"id": 1, "items": [{"item_id": 1, "amount": 10}]}
#     shipments_instance.update_shipment(1, updated_shipment)
#     assert shipments_instance.data[0]['items'][0]['amount'] == 10
#     assert 'updated_at' in shipments_instance.data[0]

# def test_remove_shipment(shipments_instance):
#     shipments_instance.data = [{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]
#     shipments_instance.remove_shipment(1)
#     assert len(shipments_instance.data) == 0

# def test_get_items_in_shipment(shipments_instance):
#     shipments_instance.data = [{"id": 1, "items": [{"item_id": 1, "amount": 5}]}]
#     items = shipments_instance.get_items_in_shipment(1)
#     assert len(items) == 1
#     assert items[0]['item_id'] == 1

#     items = shipments_instance.get_items_in_shipment(2)
#     assert items is None
