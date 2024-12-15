from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from loguru import logger

from app.database import Company, CompanyVersion
from app.schemas import CompanyCreate, CompanyUpdate

async def create_company(
    db: AsyncSession, 
    company_data: CompanyCreate, 
    user_id: str,
    change_reason: Optional[str] = None
) -> Company:
    """
    Create a new company and its initial version history record.
    """
    try:
        # Create main company record
        new_company = Company(
            **company_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        db.add(new_company)
        
        await db.flush()

        # Create initial version record
        version = CompanyVersion(
            company_id=new_company.company_id,
            version_number=1,
            changed_by=user_id,
            change_type='CREATE',
            change_reason=change_reason,
            **company_data.dict()
        )
        db.add(version)
        
        await db.commit()
        await db.refresh(new_company)
        logger.info(f"Created new company: {new_company.company_id} by user: {user_id}")
        return new_company
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating company: {str(e)}")
        raise

async def get_company(db: AsyncSession, company_id: UUID) -> Optional[Company]:
    """
    Retrieve a company by its ID.
    """
    try:
        query = select(Company).where(Company.company_id == company_id)
        result = await db.execute(query)
        company = result.scalar_one_or_none()
        if company:
            logger.info(f"Retrieved company: {company_id}")
        else:
            logger.warning(f"Company not found: {company_id}")
        return company
    except Exception as e:
        logger.error(f"Error retrieving company {company_id}: {str(e)}")
        raise

async def get_companies(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 10
) -> List[Company]:
    """
    Retrieve a list of companies with pagination.
    """
    try:
        query = select(Company).offset(skip).limit(limit)
        result = await db.execute(query)
        companies = result.scalars().all()
        logger.info(f"Retrieved {len(companies)} companies")
        return list(companies)
    except Exception as e:
        logger.error(f"Error retrieving companies: {str(e)}")
        raise

async def get_company_versions(
    db: AsyncSession, 
    company_id: UUID,
    skip: int = 0,
    limit: int = 10
) -> List[CompanyVersion]:
    """
    Retrieve version history for a specific company.
    """
    try:
        query = select(CompanyVersion)\
            .where(CompanyVersion.company_id == company_id)\
            .order_by(desc(CompanyVersion.version_number))\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        versions = result.scalars().all()
        logger.info(f"Retrieved {len(versions)} versions for company: {company_id}")
        return list(versions)
    except Exception as e:
        logger.error(f"Error retrieving company versions: {str(e)}")
        raise

async def get_latest_version_number(
    db: AsyncSession, 
    company_id: UUID
) -> int:
    """
    Get the latest version number for a company.
    """
    try:
        query = select(CompanyVersion.version_number)\
            .where(CompanyVersion.company_id == company_id)\
            .order_by(desc(CompanyVersion.version_number))\
            .limit(1)
        result = await db.execute(query)
        latest_version = result.scalar_one_or_none()
        return latest_version or 0
    except Exception as e:
        logger.error(f"Error getting latest version number: {str(e)}")
        raise

async def update_company(
    db: AsyncSession, 
    company_id: UUID, 
    update_data: CompanyUpdate,
    user_id: str,
    change_reason: Optional[str] = None
) -> Optional[Company]:
    """
    Update a company and create a new version history record.
    Only updates fields that are explicitly provided (not None).
    """
    try:
        # Get current company
        company = await get_company(db, company_id)
        if not company:
            return None

        # Filter out None values and empty strings from the update data
        update_dict = {
            k: v for k, v in update_data.model_dump(exclude_unset=True).items()
            if v is not None and v != ""
        }
        
        if not update_dict:
            raise ValueError("At least one non-empty field must be provided for update")

        # Update only the provided fields
        for key, value in update_dict.items():
            setattr(company, key, value)
        company.updated_by = user_id
        
        
        # Create new version record
        next_version = await get_latest_version_number(db, company_id) + 1
        version = CompanyVersion(
            company_id=company_id,
            version_number=next_version,
            changed_by=user_id,
            change_type='UPDATE',
            change_reason=change_reason,
            company_code=company.company_code,
            company_name=company.company_name,
            company_country=company.company_country,
            company_accounting_standards=company.company_accounting_standards
        )
        db.add(version)
        
        await db.commit()
        await db.refresh(company)
        logger.info(f"Updated company: {company_id} by user: {user_id}")
        return company
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating company: {str(e)}")
        raise

async def delete_company(
    db: AsyncSession, 
    company_id: UUID,
    user_id: str,
    change_reason: Optional[str] = None
) -> Optional[Company]:
    """
    Delete a company and all its version history records.
    Creates a final version record before deletion for audit purposes.
    """
    try:
        # Get current company
        company = await get_company(db, company_id)
        if not company:
            return None

        # Create final version record indicating deletion
        next_version = await get_latest_version_number(db, company_id) + 1
        final_version = CompanyVersion(
            company_id=company_id,
            version_number=next_version,
            changed_by=user_id,
            change_type='DELETE',
            change_reason=change_reason,
            company_code=company.company_code,
            company_name=company.company_name,
            company_country=company.company_country,
            company_accounting_standards=company.company_accounting_standards
        )
        
        # First add the final version
        db.add(final_version)
        await db.flush()  # Ensure the final version is in the session
        
        # Delete all version records
        delete_versions_query = select(CompanyVersion).where(
            CompanyVersion.company_id == company_id
        )
        versions = (await db.execute(delete_versions_query)).scalars().all()
        for version in versions:
            await db.delete(version)
        
        # Now delete the company
        await db.delete(company)
        
        # Commit all changes
        await db.commit()
        logger.info(f"Deleted company: {company_id} and all its versions by user: {user_id}")
        return company
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting company: {str(e)}")
        raise

async def restore_company_version(
    db: AsyncSession,
    company_id: UUID,
    version_number: int,
    user_id: str,
    change_reason: Optional[str] = None
) -> Optional[Company]:
    """
    Restore a company to a specific version.
    """
    try:
        # Get the specified version
        query = select(CompanyVersion)\
            .where(
                CompanyVersion.company_id == company_id,
                CompanyVersion.version_number == version_number
            )
        result = await db.execute(query)
        version = result.scalar_one_or_none()
        
        if not version:
            logger.warning(f"Version {version_number} not found for company {company_id}")
            return None
            
        # Get current company or create new if it was deleted
        company = await get_company(db, company_id)
        if not company:
            company = Company(company_id=company_id)
            db.add(company)
        
        # Restore the company data from the version
        company.company_code = version.company_code
        company.company_name = version.company_name
        company.company_country = version.company_country
        company.company_accounting_standards = version.company_accounting_standards
        company.updated_by = user_id
        
        # Create new version record for the restoration
        next_version = await get_latest_version_number(db, company_id) + 1
        new_version = CompanyVersion(
            company_id=company_id,
            version_number=next_version,
            changed_by=user_id,
            change_type='RESTORE',
            change_reason=f"Restored to version {version_number}. {change_reason or ''}",
            company_code=version.company_code,
            company_name=version.company_name,
            company_country=version.company_country,
            company_accounting_standards=version.company_accounting_standards
        )
        db.add(new_version)
        
        await db.commit()
        await db.refresh(company)
        logger.info(f"Restored company {company_id} to version {version_number} by user: {user_id}")
        return company
    except Exception as e:
        await db.rollback()
        logger.error(f"Error restoring company version: {str(e)}")
        raise

