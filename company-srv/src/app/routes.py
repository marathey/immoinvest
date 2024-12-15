from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db_session
from app.schemas import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyVersionResponse, CompanyStatusResponse, CompanyStatusCreate, CompanyStatusUpdate
from app.services import (
    create_company,
    get_company,
    get_companies,
    update_company,
    delete_company,
    get_company_versions,
    restore_company_version
)
from loguru import logger
import os

router = APIRouter()
security = HTTPBearer()

# Configuration (should be in environment variables in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-testing")
ALGORITHM = "HS256"

class AuthenticationError(Exception):
    pass

def create_test_token(user_id: str = "test-user"):
    """Create a test token - for development only"""
    data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validate JWT token and return user information"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise AuthenticationError("Could not validate credentials")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/companies", response_model=CompanyResponse)
async def create_company_endpoint(
    company: CompanyCreate,
    change_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new company."""
    logger.info(f"User {current_user['user_id']} creating new company: {company.company_name}")
    try:
        result = await create_company(
            db=db,
            company_data=company,
            user_id=current_user["user_id"],
            change_reason=change_reason
        )
        logger.success(f"Successfully created company: {result.company_id}")
        return result
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company_endpoint(
    company_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific company by ID."""
    logger.info(f"User {current_user['user_id']} fetching company with ID: {company_id}")
    company = await get_company(db, company_id)
    if not company:
        logger.warning(f"Company with ID {company_id} not found")
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List companies with pagination."""
    logger.info(f"User {current_user['user_id']} fetching companies with skip={skip}, limit={limit}")
    try:
        companies = await get_companies(db, skip, limit)
        logger.success(f"Successfully fetched {len(companies)} companies")
        return companies
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company_endpoint(
    company_id: UUID,
    company: CompanyUpdate,
    change_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update an existing company."""
    logger.info(f"User {current_user['user_id']} updating company with ID: {company_id}")
    try:
        # The CompanyUpdate schema now validates that at least one field is provided
        updated_company = await update_company(
            db=db,
            company_id=company_id,
            update_data=company,
            user_id=current_user["user_id"],
            change_reason=change_reason
        )
        if not updated_company:
            logger.warning(f"Company with ID {company_id} not found")
            raise HTTPException(status_code=404, detail="Company not found")
        
        logger.success(f"Successfully updated company: {company_id}")
        return updated_company
    except ValueError as ve:
        logger.error(f"Validation error while updating company: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        

@router.delete("/companies/{company_id}", response_model=CompanyResponse)
async def delete_company_endpoint(
    company_id: UUID,
    change_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a company."""
    logger.info(f"User {current_user['user_id']} deleting company with ID: {company_id}")
    try:
        deleted_company = await delete_company(
            db=db,
            company_id=company_id,
            user_id=current_user["user_id"],
            change_reason=change_reason
        )
        if not deleted_company:
            logger.warning(f"Company with ID {company_id} not found")
            raise HTTPException(status_code=404, detail="Company not found")
        logger.success(f"Successfully deleted company: {company_id}")
        return deleted_company
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/{company_id}/versions", response_model=List[CompanyVersionResponse])
async def get_company_versions_endpoint(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get version history for a company."""
    logger.info(f"User {current_user['user_id']} fetching version history for company: {company_id}")
    try:
        versions = await get_company_versions(db, company_id, skip, limit)
        logger.success(f"Successfully fetched {len(versions)} versions for company: {company_id}")
        return versions
    except Exception as e:
        logger.error(f"Error fetching company versions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/{company_id}/restore/{version_number}", response_model=CompanyResponse)
async def restore_company_version_endpoint(
    company_id: UUID,
    version_number: int,
    change_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Restore a company to a specific version."""
    logger.info(f"User {current_user['user_id']} restoring company {company_id} to version {version_number}")
    try:
        restored_company = await restore_company_version(
            db=db,
            company_id=company_id,
            version_number=version_number,
            user_id=current_user["user_id"],
            change_reason=change_reason
        )
        if not restored_company:
            logger.warning(f"Version {version_number} not found for company {company_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_number} not found for company {company_id}"
            )
        logger.success(f"Successfully restored company {company_id} to version {version_number}")
        return restored_company
    except Exception as e:
        logger.error(f"Error restoring company version: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper endpoint for development to get a test token
@router.get("/debug/get-test-token", include_in_schema=os.getenv("ENVIRONMENT") == "development")
async def get_test_token():
    """Get a test token for development purposes"""
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=404, detail="Not found")
    return {"token": create_test_token()}


# In routes.py
@router.post("/company-statuses", response_model=CompanyStatusResponse)
async def create_company_status_endpoint(
    status: CompanyStatusCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new company status type."""
    return await create_company_status(db, status, user_id=current_user["user_id"])

@router.get("/company-statuses", response_model=List[CompanyStatusResponse])
async def list_company_statuses(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """List all company statuses."""
    return await get_company_statuses(db, active_only)

@router.get("/company-statuses/{status_id}", response_model=CompanyStatusResponse)
async def get_company_status_endpoint(
    status_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific company status."""
    status = await get_company_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@router.put("/company-statuses/{status_id}", response_model=CompanyStatusResponse)
async def update_company_status_endpoint(
    status_id: UUID,
    status: CompanyStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a company status type."""
    updated_status = await update_company_status_type(db, status_id, status, user_id=current_user["user_id"])
    if not updated_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return updated_status