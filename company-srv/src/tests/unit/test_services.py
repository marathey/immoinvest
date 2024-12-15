import pytest
from uuid import UUID
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.company_service import create_company, update_company, delete_company
from app.schemas.company_schema import CompanyCreate, CompanyUpdate
from app.database.models.company import Company
from app.database.models.company_version import CompanyVersion

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    mock = AsyncMock(spec=AsyncSession)
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_update_company(mock_db):
    """Test company update service"""
    # Arrange
    company_id = UUID("12345678-1234-5678-1234-567812345678")  # Convert to UUID
    update_data = CompanyUpdate(company_name="Updated Company")
    user_id = "test-user"
    
    # Mock the get_company function
    existing_company = Company(
        company_code="TEST001",
        company_name="Original Company",
        company_country="US",
        company_accounting_standards="GAAP",
        created_by="test-user",
        updated_by="test-user"
    )
    
    # Setup mocks
    with patch('app.services.company_service.get_company', 
               new_callable=AsyncMock) as mock_get_company, \
         patch('app.services.company_service.get_latest_version_number',
               new_callable=AsyncMock) as mock_get_version:
        
        # Configure mocks
        mock_get_company.return_value = existing_company
        mock_get_version.return_value = 0  # This will make next_version = 1
        
        # Act
        result = await update_company(
            db=mock_db,
            company_id=company_id,
            update_data=update_data,
            user_id=user_id
        )
        
        # Assert
        assert result.company_name == "Updated Company"
        assert result.updated_by == user_id
        
        # Verify version was created
        assert mock_db.add.call_count == 1
        version = mock_db.add.call_args.args[0]
        assert isinstance(version, CompanyVersion)
        assert version.version_number == 1
        assert version.company_id == company_id
        assert version.company_code == existing_company.company_code
        assert version.company_name == existing_company.company_name
        assert version.company_country == existing_company.company_country
        assert version.company_accounting_standards == existing_company.company_accounting_standards
        assert version.change_type == "UPDATE"
        assert version.changed_by == user_id
        
        # Verify DB operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(existing_company)

@pytest.mark.asyncio
async def test_update_company_not_found(mock_db):
    """Test update company when company doesn't exist"""
    # Arrange
    company_id = UUID("12345678-1234-5678-1234-567812345678")
    update_data = CompanyUpdate(company_name="Updated Company")
    user_id = "test-user"
    
    with patch('app.services.company_service.get_company', 
               new_callable=AsyncMock) as mock_get_company:
        # Configure mock to return None (company not found)
        mock_get_company.return_value = None
        
        # Act
        result = await update_company(
            db=mock_db,
            company_id=company_id,
            update_data=update_data,
            user_id=user_id
        )
        
        # Assert
        assert result is None
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_update_company_no_changes(mock_db):
    """Test update company with no actual changes"""
    # Arrange
    company_id = UUID("12345678-1234-5678-1234-567812345678")
    update_data = CompanyUpdate()  # Empty update
    user_id = "test-user"
    
    existing_company = Company(
        company_code="TEST001",
        company_name="Original Company",
        company_country="US",
        company_accounting_standards="GAAP",
        created_by="test-user",
        updated_by="test-user"
    )
    
    with patch('app.services.company_service.get_company', 
               new_callable=AsyncMock) as mock_get_company:
        mock_get_company.return_value = existing_company
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await update_company(
                db=mock_db,
                company_id=company_id,
                update_data=update_data,
                user_id=user_id
            )
        
        assert str(exc_info.value) == "At least one non-empty field must be provided for update"
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()