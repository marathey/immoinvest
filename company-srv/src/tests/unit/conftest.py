# tests/unit/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def mock_db():
    """Provide a mock database session for unit tests"""
    mock = AsyncMock(spec=AsyncSession)
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    mock.rollback = AsyncMock()
    return mock

@pytest.fixture
def sample_company_data():
    """Provide sample company data for tests"""
    return {
        "company_id": uuid4(),
        "company_code": "TEST001",
        "company_name": "Test Company",
        "company_country": "US",
        "company_accounting_standards": "GAAP",
        "created_by": "test-user",
        "updated_by": "test-user",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_external_services():
    """Mock external service dependencies"""
    mock = AsyncMock()
    mock.log_audit_event = AsyncMock()
    mock.send_notification = AsyncMock()
    return mock