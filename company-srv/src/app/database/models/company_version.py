import uuid
from sqlalchemy import Column, String, TIMESTAMP, UUID, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from ..config import Base, DATABASE_SCHEMA

class CompanyVersion(Base):
    __tablename__ = "company_versions"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.companies.company_id" if DATABASE_SCHEMA else "companies.company_id"))
    version_number = Column(Integer, nullable=False)
    
    company_code = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_country = Column(String, nullable=False)
    company_accounting_standards = Column(String, nullable=False)
    
    changed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(String, nullable=False)
    change_type = Column(String, nullable=False)
    change_reason = Column(String, nullable=True)
    
    status_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.company_statuses.status_id" if DATABASE_SCHEMA else "company_statuses.status_id"))
    status_reason = Column(String, nullable=True)

    company = relationship("Company", back_populates="versions")