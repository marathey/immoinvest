from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from loguru import logger

from app.database import CompanyStatus
from app.schemas import CompanyStatusCreate, CompanyStatusUpdate


# In services.py
async def create_company_status(
    db: AsyncSession,
    status_data: CompanyStatusCreate,
    user_id: str
) -> CompanyStatus:
    """Create a new company status."""
    try:
        new_status = CompanyStatus(
            **status_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        db.add(new_status)
        await db.commit()
        await db.refresh(new_status)
        return new_status
    except Exception as e:
        await db.rollback()
        raise

async def get_company_status(
    db: AsyncSession, 
    status_id: UUID
) -> Optional[CompanyStatus]:
    """Get a specific company status."""
    query = select(CompanyStatus).where(CompanyStatus.status_id == status_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_company_statuses(
    db: AsyncSession,
    active_only: bool = True
) -> List[CompanyStatus]:
    """Get all company statuses."""
    query = select(CompanyStatus)
    if active_only:
        query = query.where(CompanyStatus.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())

async def update_company_status_type(
    db: AsyncSession,
    status_id: UUID,
    status_data: CompanyStatusUpdate,
    user_id: str
) -> Optional[CompanyStatus]:
    """Update a company status type."""
    status = await get_company_status(db, status_id)
    if not status:
        return None
        
    update_dict = status_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(status, key, value)
    status.updated_by = user_id
    
    await db.commit()
    await db.refresh(status)
    return status