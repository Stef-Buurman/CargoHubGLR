from unittest.mock import Mock
import pytest
from app.models.v2.supplier import Supplier
from app.services.v2.model_services.suppliers_service import SupplierService
from tests.test_globals import *


TEST_SUPPLIERS = [
            Supplier(
                id=1,
                code="SUP0001",
                name="Lee, Parks and Johnson",
                address="5989 Sullivan Drives",
                address_extra="Apt. 996",
                city="Port Anitaburgh",
                zip_code="91688",
                province="Illinois",
                country="Czech Republic",
                contact_name="Toni Barnett",
                phonenumber="363.541.7282x36825",
                reference="LPaJ-SUP0001",
                created_at="1971-10-20 18:06:17",
                updated_at="1985-06-08 00:13:46",
                is_archived=False,
            ),
            Supplier(
                id=2,
                code="SUP0002",
                name="Holden-Quinn",
                address="576 Christopher Roads",
                address_extra="Suite 072",
                city="Amberbury",
                zip_code="16105",
                province="Illinois",
                country="Saint Martin",
                contact_name="Kathleen Vincent",
                phonenumber="001-733-291-8848x3542",
                reference="H-SUP0002",
                created_at="1995-12-18 03:05:46",
                updated_at="2019-11-10 22:11:12",
                is_archived=False,
            ),
            Supplier(
                id=3,
                code="SUP0003",
                name="White and Sons",
                address="1761 Shepard Valley",
                address_extra="Suite 853",
                city="Aguilarton",
                zip_code="63918",
                province="Wyoming",
                country="Ghana",
                contact_name="Jason Hudson",
                phonenumber="001-910-585-6962x8307",
                reference="WaS-SUP0003",
                created_at="2010-06-14 02:32:58",
                updated_at="2019-06-16 19:29:49",
                is_archived=True,
            ),
        ]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def supplier_service(mock_db_service):
    """Fixture to create an SupplierService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_SUPPLIERS
    service = SupplierService(mock_db_service)
    return service


def test_get_all_suppliers(supplier_service, mock_db_service):
    suppliers = supplier_service.get_all_suppliers()

    assert len(suppliers) == len(supplier_service.data)
    assert suppliers[0].name == "Lee, Parks and Johnson"
    assert mock_db_service.get_all.call_count == 2


def test_get_suppliers(supplier_service):
    suppliers = supplier_service.get_suppliers()

    assert len(suppliers) == 2
    assert all(not supplier.is_archived for supplier in suppliers)


def test_get_supplier(supplier_service, mock_db_service):
    supplier_id = 1
    supplier = supplier_service.get_supplier(supplier_id)

    assert supplier.id == supplier_id
    assert mock_db_service.get.call_count == 0


def test_get_supplier_from_db(supplier_service, mock_db_service):
    mock_db_service.get.return_value = Supplier(
        id=4,
        code="SUP0004",
        name="Holden-Quinn",
        address="576 Christopher Roads",
        address_extra="Suite 072",
        city="Amberbury",
        zip_code="16105",
        province="Illinois",
        country="Saint Martin",
        contact_name="Kathleen Vincent",
        phonenumber="001-733-291-8848x3542",
        reference="H-SUP0002",
        created_at="1995-12-18 03:05:46",
        updated_at="2019-11-10 22:11:12",
        is_archived=False,
    )
    supplier = supplier_service.get_supplier(4)

    assert supplier.id == 4
    assert mock_db_service.get.call_count == 1


def test_add_supplier(supplier_service, mock_db_service):
    new_supplier = Supplier(
        code="SUP0010",
        name="Holden-Quinn019912u3912y7egawjhdb ahs bcasnhf sjdhbsdh fcdhy",
        address="576 Christopher Roads",
        address_extra="Suite 072",
        city="Amberbury",
        zip_code="16105",
        province="Illinois",
        country="Saint Martin",
        contact_name="Kathleen Vincent",
        phonenumber="001-733-291-8848x3542",
        reference="H-SUP0002",
        created_at="1995-12-18 03:05:46",
        updated_at="2019-11-10 22:11:12",
        is_archived=False,
    )
    mock_db_service.insert.return_value = new_supplier

    result = supplier_service.add_supplier(new_supplier)

    assert mock_db_service.insert.call_count == 1
    assert new_supplier in supplier_service.data
    assert result.name == new_supplier.name


def test_update_supplier(supplier_service, mock_db_service):
    supplier_id = 1
    supplier = supplier_service.get_supplier(supplier_id)
    assert mock_db_service.get.call_count == 0
    assert supplier is not None

    updated_supplier = supplier.copy(update={"name": "Updated Type A"})
    mock_db_service.update.return_value = updated_supplier

    result = supplier_service.update_supplier(supplier_id, updated_supplier)

    assert mock_db_service.update.call_count == 1
    assert result.name == "Updated Type A"
    updated_supplier = supplier_service.get_supplier(supplier_id)
    assert updated_supplier.name == "Updated Type A"


def test_update_supplier_archived(supplier_service, mock_db_service):
    supplier_id = 1
    supplier = supplier_service.get_supplier(supplier_id)
    assert mock_db_service.get.call_count == 0
    assert supplier is not None

    mock_db_service.update.return_value = supplier.copy(update={"is_archived": True})

    updatedsupplier = supplier_service.archive_supplier(supplier_id)
    assert updatedsupplier.is_archived == True
    assert mock_db_service.update.call_count == 1

    updated_supplier = supplier.copy(update={"name": "naame"})

    result = supplier_service.update_supplier(supplier_id, updated_supplier)

    assert mock_db_service.update.call_count == 1
    assert result is None
    updated_supplier = supplier_service.get_supplier(supplier_id)
    assert updated_supplier.is_archived


def test_archive_supplier(supplier_service, mock_db_service):
    supplier_id = 1
    supplier = supplier_service.get_supplier(supplier_id)
    mock_db_service.update.return_value = supplier

    result = supplier_service.archive_supplier(supplier_id)

    assert mock_db_service.update.call_count == 1
    assert result.is_archived
    new_supplier = supplier_service.get_supplier(supplier_id)
    assert new_supplier.is_archived


def test_archive_supplier_not_found(supplier_service, mock_db_service):
    supplier_id = non_existent_id
    result = supplier_service.archive_supplier(supplier_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_supplier(supplier_service, mock_db_service):
    supplier_id = 1
    supplier = supplier_service.get_supplier(supplier_id)
    mock_db_service.update.return_value = supplier

    result = supplier_service.unarchive_supplier(supplier_id)

    assert mock_db_service.update.call_count == 1
    assert not result.is_archived
    new_supplier = supplier_service.get_supplier(supplier_id)
    assert not new_supplier.is_archived


def test_unarchive_supplier_not_found(supplier_service, mock_db_service):
    supplier_id = non_existent_id
    result = supplier_service.unarchive_supplier(supplier_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_supplier_archived(supplier_service):
    assert supplier_service.is_supplier_archived(1) is False
    assert supplier_service.is_supplier_archived(3) is True
    assert supplier_service.is_supplier_archived(99) is None
