import uuid
from sqlalchemy import Column, String, TIMESTAMP, UUID, Boolean, func
from sqlalchemy.orm import relationship
from ..config import Base, DATABASE_SCHEMA

class CompanyStatus(Base):
    __tablename__ = "company_statuses"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_code = Column(String, nullable=False, unique=True)
    status_description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String, nullable=False)
    
    companies = relationship("Company", back_populates="status")

    def __init__(self, **kwargs):
        # Set default value for is_active if not provided
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        super().__init__(**kwargs)