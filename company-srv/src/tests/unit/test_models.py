import pytest
from datetime import datetime
from uuid import UUID, uuid4
from app.database.models.company import Company
from app.database.models.company_status import CompanyStatus
from app.database.models.company_version import CompanyVersion

def test_company_model_initialization():
    """Test Company model creation with required fields"""
    test_id = uuid4()
    company = Company(
        company_id=test_id,
        company_code="TEST001",
        company_name="Test Company",
        company_country="US",
        company_accounting_standards="GAAP",
        created_by="test-user",
        updated_by="test-user"
    )
    
    assert isinstance(company.company_id, UUID)
    assert company.company_id == test_id
    assert company.company_code == "TEST001"
    assert company.company_name == "Test Company"
    assert company.company_country == "US"
    assert company.company_accounting_standards == "GAAP"
    assert company.created_by == "test-user"
    assert company.updated_by == "test-user"
    
    assert company.status_id is None
    assert company.status_reason is None
    assert company.status_changed_at is None
    assert company.status is None
    assert isinstance(company.versions, list)
    assert len(company.versions) == 0

def test_company_status_model_initialization():
    """Test CompanyStatus model creation with explicit values"""
    test_id = uuid4()
    status = CompanyStatus(
        status_id=test_id,
        status_code="ACTIVE",
        status_description="Active company status",
        created_by="test-user",
        updated_by="test-user",
        is_active=True
    )
    
    assert isinstance(status.status_id, UUID)
    assert status.status_id == test_id
    assert status.status_code == "ACTIVE"
    assert status.created_by == "test-user"
    assert status.updated_by == "test-user"
    assert status.status_description == "Active company status"
    assert status.is_active is True
    assert isinstance(status.companies, list)
    assert len(status.companies) == 0

def test_company_status_model_default_values():
    """Test CompanyStatus model with default values"""
    test_id = uuid4()
    status = CompanyStatus(
        status_id=test_id,
        status_code="ACTIVE",
        created_by="test-user",
        updated_by="test-user"
    )
    
    assert status.is_active is True  # Should now work with Python-level default
    assert status.status_description is None

def test_company_status_model_override_defaults():
    """Test CompanyStatus model with overridden default values"""
    test_id = uuid4()
    status = CompanyStatus(
        status_id=test_id,
        status_code="INACTIVE",
        created_by="test-user",
        updated_by="test-user",
        is_active=False
    )
    
    assert status.is_active is False
    assert status.status_description is None

def test_company_version_model_initialization():
    """Test CompanyVersion model creation"""
    version_id = uuid4()
    company_id = uuid4()
    status_id = uuid4()
    
    version = CompanyVersion(
        version_id=version_id,
        company_id=company_id,
        version_number=1,
        company_code="TEST001",
        company_name="Test Company",
        company_country="US",
        company_accounting_standards="GAAP",
        changed_by="test-user",
        change_type="CREATE",
        status_id=status_id,
        status_reason="Initial creation",
        change_reason="New company creation"
    )
    
    assert isinstance(version.version_id, UUID)
    assert version.version_id == version_id
    assert version.company_id == company_id
    assert version.version_number == 1
    assert version.company_code == "TEST001"
    assert version.company_name == "Test Company"
    assert version.company_country == "US"
    assert version.company_accounting_standards == "GAAP"
    assert version.changed_by == "test-user"
    assert version.change_type == "CREATE"
    assert version.status_id == status_id
    assert version.status_reason == "Initial creation"
    assert version.change_reason == "New company creation"

def test_company_relationships():
    """Test relationships between Company, CompanyStatus, and CompanyVersion"""
    company = Company(
        company_id=uuid4(),
        company_code="TEST001",
        company_name="Test Company",
        company_country="US",
        company_accounting_standards="GAAP",
        created_by="test-user",
        updated_by="test-user"
    )
    
    status = CompanyStatus(
        status_id=uuid4(),
        status_code="ACTIVE",
        status_description="Active company status",
        created_by="test-user",
        updated_by="test-user"
    )
    
    version = CompanyVersion(
        version_id=uuid4(),
        company_id=company.company_id,
        version_number=1,
        company_code=company.company_code,
        company_name=company.company_name,
        company_country=company.company_country,
        company_accounting_standards=company.company_accounting_standards,
        changed_by="test-user",
        change_type="CREATE"
    )
    
    company.status = status
    company.versions.append(version)
    
    assert company.status is status
    assert company in status.companies
    assert version in company.versions
    assert version.company is company