from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import create_db_engine

# A fixed Monday in the future so slot dates never depend on the real clock.
REF_MONDAY = date(2030, 1, 7)
NOW = datetime(2030, 1, 7, 8, 0)


@pytest.fixture
def engine():
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def seeded(session):
    """One week of slots starting REF_MONDAY, nothing pre-booked."""
    seed_database(session, start=REF_MONDAY, days=7, prebook_ratio=0.0)
    return session


@pytest.fixture(scope="session")
def classifier(tmp_path_factory):
    """Intent classifier trained from intents.yaml into a temp dir (not the committed model)."""
    from app.nlu.classifier import IntentClassifier
    from app.nlu.train import fit_and_save

    path = tmp_path_factory.mktemp("nlu") / "nlu.joblib"
    fit_and_save(path)
    return IntentClassifier(path)


# Monday 7 January 2030, before opening: every slot of the month is in the future.
CALL_NOW = datetime(2030, 1, 7, 8, 0)


@pytest.fixture
def clinic(session):
    """A month of free slots from REF_MONDAY (nothing pre-booked)."""
    seed_database(session, start=REF_MONDAY, days=31, prebook_ratio=0.0)
    return session


@pytest.fixture
def call(clinic, classifier):
    """Start a phone call: ``c = call(); c.say("...")``."""
    from tests.conversation import Call

    def start(now: datetime = CALL_NOW) -> Call:
        return Call(clinic, classifier, now)

    return start
