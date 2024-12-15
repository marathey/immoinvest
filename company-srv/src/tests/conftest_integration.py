import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Dict
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime
import pytest_asyncio  # Add this import
import asyncio

from app.database import (
    setup_db,
    get_db_session,
    engine,
    async_session,
    Company,  # if needed
    CompanyVersion,  # if needed
    CompanyStatus   # if needed
)
from app.database import get_db_session
from app.api import app
from app.auth import create_test_token

import os

# Use SQLite for testing
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@0.0.0.0:5433/test_db?ssl=disable"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["DATABASE_SCHEMA"] = "COMPANY_MASTER_DATA"

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Run database setup before any tests"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_db())

@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
    )
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session

@pytest.fixture
def client(async_session) -> TestClient:
    def override_get_db():
        return async_session

    app.dependency_overrides[get_db_session] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_token():
    return create_test_token("test-user")

@pytest.fixture
def auth_headers(test_token):
    return {"Authorization": f"Bearer {test_token}"}