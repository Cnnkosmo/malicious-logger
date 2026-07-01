from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer  # pyright: ignore[reportMissingTypeStubs]


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:  # pyright: ignore[reportMissingTypeStubs]
    with PostgresContainer("postgres:16-alpine") as pg:  # pyright: ignore[reportMissingTypeStubs]
        yield pg


@pytest.fixture(scope="session")
def db_engine(postgres_container: Any) -> Generator[Engine, None, None]:
    engine = create_engine(postgres_container.get_connection_url())
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_url(postgres_container: Any) -> str:
    return str(postgres_container.get_connection_url())


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    with Session(db_engine) as session:
        yield session
        session.rollback()


@pytest.fixture(scope="session", autouse=True)
def verify_db(db_engine: Engine) -> None:
    """Smoke-check the container is actually reachable."""
    with db_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
