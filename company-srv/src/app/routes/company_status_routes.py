from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.database import get_db_session
from app.schemas import CompanyStatusResponse, CompanyStatusCreate, CompanyStatusUpdate
from app.services import (
    create_company_status,
    get_company_statuses,
    get_company_status,
    update_company_status_type
)
from app.auth import get_current_user
from loguru import logger

router = APIRouter(prefix="/company-status",
    tags=["Company Status"]
    )

@router.post("/", response_model=CompanyStatusResponse)
async def create_company_status_endpoint(
    status: CompanyStatusCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new company status type."""
    return await create_company_status(db, status, user_id=current_user["user_id"])

@router.get("/", response_model=List[CompanyStatusResponse])
async def list_company_statuses(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """List all company statuses."""
    return await get_company_statuses(db, active_only)

@router.get("/{status_id}", response_model=CompanyStatusResponse)
async def get_company_status_endpoint(
    status_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific company status."""
    status = await get_company_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@router.put("/{status_id}", response_model=CompanyStatusResponse)
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