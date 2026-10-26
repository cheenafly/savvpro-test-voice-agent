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
