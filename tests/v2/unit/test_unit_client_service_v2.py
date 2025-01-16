from unittest.mock import Mock
import pytest
from app.models.v2.client import Client
from app.services.v2.model_services.client_service import ClientService
from tests.test_globals import *


TEST_CLIENTS = [
    Client(
        id=1,
        name="Raymond Inc",
        address="1296 Daniel Road Apt. 349",
        city="Pierceview",
        zip_code="28301",
        province="Colorado",
        country="United States",
        contact_name="Bryan Clark",
        contact_phone="242.732.3483x2573",
        contact_email="robertcharles@example.net",
        created_at="2010-04-28 02:22:53",
        updated_at="2022-02-09 20:22:35",
        is_archived=False,
    ),
    Client(
        id=2,
        name="Williams Ltd",
        address="2989 Flores Turnpike Suite 012",
        city="Lake Steve",
        zip_code="08092",
        province="Arkansas",
        country="United States",
        contact_name="Megan Hayden",
        contact_phone="8892853366",
        contact_email="qortega@example.net",
        created_at="1973-02-24 07:36:32",
        updated_at="2014-06-20 17:46:19",
        is_archived=True,
    ),
    Client(
        id=3,
        name="Parker, Campos and Rodriguez",
        address="502 Andrews Groves Suite 919",
        city="West Michael",
        zip_code="54265",
        province="Kansas",
        country="United States",
        contact_name="Tracey Mendoza",
        contact_phone="+1-256-833-2925x60006",
        contact_email="stevenpowers@example.net",
        created_at="2020-04-24 06:41:57",
        updated_at="2021-08-18 08:14:08",
        is_archived=False,
    ),
]


@pytest.fixture
def mock_db_service():
    """Fixture to create a mocked DatabaseService."""
    return Mock()


@pytest.fixture
def client_service(mock_db_service):
    """Fixture to create an ClientService instance with the mocked DatabaseService."""
    mock_db_service.get_all.return_value = TEST_CLIENTS
    service = ClientService(mock_db_service, True)
    return service


def test_get_all_clients(client_service, mock_db_service):
    clients = client_service.get_all_clients()

    assert len(clients) == len(client_service.data)
    assert clients[0].name == "Raymond Inc"
    assert mock_db_service.get_all.call_count == 2


def test_get_clients(client_service):
    clients = client_service.get_clients()

    assert len(clients) == 2
    assert all(not client.is_archived for client in clients)


def test_get_client(client_service, mock_db_service):
    client_id = 1
    client = client_service.get_client(client_id)

    assert client.id == client_id
    assert mock_db_service.get.call_count == 0


def test_get_client_not_found(client_service, mock_db_service):
    mock_db_service.get.return_value = None
    assert client_service.get_client(non_existent_id) is None
    assert mock_db_service.get.call_count == 1


def test_get_client_from_db(client_service, mock_db_service):
    client_from_db = Client(
        id=5,
        name="Mccormick LLC",
        address="6409 Morris Terrace",
        city="North Glenda",
        zip_code="07992",
        province="Arizona",
        country="United States",
        contact_name="Mr. Joseph Morales",
        contact_phone="358-492-9708x998",
        contact_email="leonard32@example.net",
        created_at="1979-05-01 03:25:35",
        updated_at="2017-08-03 08:10:08",
        is_archived=False,
    )
    mock_db_service.get.return_value = client_from_db

    client = client_service.get_client(5)

    assert client.id == 5
    assert mock_db_service.get.call_count == 1
    assert client == client_from_db


def test_add_client(client_service, mock_db_service):
    client = Client(
        id=4,
        name="Doe Ltd",
        address="1234 Main Street",
        city="Anytown",
        zip_code="12345",
        province="Texas",
        country="United States",
        contact_name="John Doe",
        contact_phone="123-456-7890",
        contact_email="johndoe@example.net",
        created_at="2022-02-09 20:22:35",
        updated_at="2022-02-09 20:22:35",
    )
    mock_db_service.insert.return_value = client.model_copy(update={"id": 5})
    result = client_service.add_client(client)

    assert result.id == 5
    assert mock_db_service.insert.call_count == 1


def test_update_client(client_service, mock_db_service):
    client = Client(
        id=1,
        name="Raymond Inc",
        address="1296 Daniel Road Apt. 349",
        city="Pierceview",
        zip_code="28301",
        province="Colorado",
        country="United States",
        contact_name="Bryan Clark",
        contact_phone="242.732.3483x2573",
        contact_email="test@mail.com",
        created_at="2010-04-28 02:22:53",
        updated_at="2022-02-09 20:22:35",
    )
    mock_db_service.update.return_value = client
    result = client_service.update_client(client.id, client)

    assert result.id == client.id
    assert client.model_copy(update={"updated_at": result.updated_at}) == result
    assert mock_db_service.update.call_count == 1


def test_update_client_archived(client_service, mock_db_service):
    client = Client(
        id=2,
        name="Williams Ltd",
        address="2989 Flores Turnpike Suite 012",
        city="Lake Steve",
        zip_code="08092",
        province="Arkansas",
        country="United States",
        contact_name="Megan Hayden",
        contact_phone="8892853366",
        contact_email="test@mail2.com",
        created_at="1973-02-24 07:36:32",
        updated_at="2014-06-20 17:46:19",
        is_archived=True,
    )
    result = client_service.update_client(client.id, client)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_client_archived(client_service, mock_db_service):
    client_id = 2
    client = client_service.get_client(client_id)
    assert client is not None

    assert client_service.is_client_archived(client_id)
    assert mock_db_service.get.call_count == 0


def test_is_client_archived_not_found(client_service, mock_db_service):
    assert not client_service.is_client_archived(non_existent_id)
    assert mock_db_service.get.call_count == 0


def test_archive_client(client_service, mock_db_service):
    client_id = 1
    client = client_service.get_client(client_id)
    assert client is not None

    mock_db_service.update.return_value = client.model_copy(
        update={"is_archived": True}
    )

    result = client_service.archive_client(client_id)

    assert result.is_archived == True
    assert mock_db_service.update.call_count == 1


def test_archive_client_not_found(client_service, mock_db_service):
    result = client_service.archive_client(non_existent_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_unarchive_client(client_service, mock_db_service):
    client_id = 1
    client = client_service.get_client(client_id)
    assert client is not None

    client.is_archived = True
    mock_db_service.update.return_value = client

    result = client_service.unarchive_client(client_id)

    assert not result.is_archived
    assert mock_db_service.update.call_count == 1


def test_unarchive_client_not_found(client_service, mock_db_service):
    result = client_service.unarchive_client(non_existent_id)

    assert result is None
    assert mock_db_service.update.call_count == 0


def test_is_client_archived(client_service):
    assert client_service.is_client_archived(1) is False
    assert client_service.is_client_archived(3) is False
    assert client_service.is_client_archived(99) is None
