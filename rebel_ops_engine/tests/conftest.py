import pytest

from agents.calendar import CalendarAgent
from agents.encryption import YodaEncryptionAgent
from agents.error_handler import ErrorProtocolAgent
from agents.reporter import ReportingAgent
from agents.router import RoutingAgent
from models import Channel, Message


@pytest.fixture(autouse=True)
def clean_db():
    import main as main_module
    main_module.db.reset_all()


@pytest.fixture
def base_message():
    return Message(
        channel=Channel.INTERGALACTIC_WHATSAPP,
        sender="Test Sender",
        content="This is a test message.",
    )


@pytest.fixture
def fresh_router():
    r = RoutingAgent()
    yield r
    r.reset()


@pytest.fixture
def fresh_reporter():
    r = ReportingAgent()
    yield r
    r.reset()


@pytest.fixture
def fresh_calendar():
    c = CalendarAgent()
    yield c
    c.reset()


@pytest.fixture
def fresh_encryption():
    e = YodaEncryptionAgent()
    yield e
    e.reset()


@pytest.fixture
def fresh_error_handler():
    e = ErrorProtocolAgent()
    yield e
    e.reset()
