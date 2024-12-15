import uuid
from sqlalchemy import Column, String, TIMESTAMP, UUID, ForeignKey, func
from sqlalchemy.orm import relationship
from ..config import Base, DATABASE_SCHEMA

class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_code = Column(String, nullable=False, unique=True)
    company_name = Column(String, nullable=False)
    company_country = Column(String, nullable=False)
    company_accounting_standards = Column(String, nullable=False)
    
    status_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.company_statuses.status_id" if DATABASE_SCHEMA else "company_statuses.status_id"))
    status = relationship("CompanyStatus", back_populates="companies")
    status_reason = Column(String, nullable=True)
    status_changed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String, nullable=False)
    
    versions = relationship("CompanyVersion", back_populates="company")