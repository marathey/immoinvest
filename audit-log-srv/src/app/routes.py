from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.database import get_db_session, AuditLog
from app.schemas import AuditLogEntry
from loguru import logger
from datetime import datetime

router = APIRouter()

@router.post("/audit-logs/", status_code=201)
async def create_audit_log(log_entry: AuditLogEntry, db: AsyncSession = Depends(get_db_session)):
    try:
        new_log = AuditLog(**log_entry.dict())
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        logger.info(f"Audit Log Entry: '{AuditLogEntry}'.")
        return {"log_id": new_log.id, "message": "Audit log entry created successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create audit log entry: {AuditLogEntry}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs/", response_model=List[AuditLogEntry])
async def get_audit_logs(
    service_name: Optional[str] = None,
    service_id: Optional[str] = None,
    user_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    time_from: Optional[datetime] = None,
    time_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        # Default time_from to the current time if not provided
        time_to = time_to or datetime.utcnow()

        # Build the base query
        query = select(AuditLog)

        # Apply filters based on query parameters
        if service_name:
            query = query.filter(AuditLog.service_name == service_name)
        if service_id:
            query = query.filter(AuditLog.service_id == service_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if time_from:
            query = query.filter(AuditLog.timestamp >= time_from)
        if time_to:
            query = query.filter(AuditLog.timestamp <= time_to)
        # Log the query for debugging
        logger.info(f"Executing Audit Log Query: {query}")

        # Execute the query
        result = await db.execute(query)
        logs = result.scalars().all()
        # Log the results
        if logs:
            logger.info(f"Query Results: {len(logs)} records found.")
            for log in logs:
                logger.debug(f"Record: {log}")
        else:
            logger.info("No records found for the given query.")
        return logs
    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"Failed to fetch audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
