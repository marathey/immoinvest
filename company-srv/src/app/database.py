import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, String, JSON, TIMESTAMP, text, UUID, MetaData, Integer,ForeignKey, func, Boolean
from sqlalchemy.schema import CreateSchema
from loguru import logger
import uuid
from dotenv import load_dotenv

Base = declarative_base()

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Define custom metadata with schema support
metadata = MetaData(schema=DATABASE_SCHEMA) if DATABASE_SCHEMA else MetaData()

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Enables connection health checks
    pool_size=5,         # Set connection pool size
    max_overflow=10,     # Maximum number of connections to create beyond pool_size
    connect_args={
        "server_settings": {
            "application_name": "company-service"  # Helps with debugging
        }
    }
)

logger.info("Database engine created with URL: {}", DATABASE_URL)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_code = Column(String, nullable=False, unique=True)
    company_name = Column(String, nullable=False)
    company_country = Column(String, nullable=False)
    company_accounting_standards = Column(String, nullable=False)
    
    # Status relationship
    status_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.company_statuses.status_id" if DATABASE_SCHEMA else "company_statuses.status_id"))
    status = relationship("CompanyStatus", back_populates="companies")
    status_reason = Column(String, nullable=True)
    status_changed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Audit fields in main table
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String, nullable=False)
    
    # Relationship to version history
    versions = relationship("CompanyVersion", back_populates="company")

class CompanyVersion(Base):
    __tablename__ = "company_versions"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.companies.company_id" if DATABASE_SCHEMA else "companies.company_id"))
    version_number = Column(Integer, nullable=False)
    
    # Company fields at this version
    company_code = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_country = Column(String, nullable=False)
    company_accounting_standards = Column(String, nullable=False)
    
    # Version metadata
    changed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    changed_by = Column(String, nullable=False)
    change_type = Column(String, nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    change_reason = Column(String, nullable=True)
    
    # Company Status
    status_id = Column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.company_statuses.status_id" if DATABASE_SCHEMA else "company_statuses.status_id"))
    status_reason = Column(String, nullable=True)

    # Relationship back to company
    company = relationship("Company", back_populates="versions")

class CompanyStatus(Base):
    __tablename__ = "company_statuses"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None
    
    status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_code = Column(String, nullable=False, unique=True)
    status_name = Column(String, nullable=False)
    status_description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(String, nullable=False)
    
    # Relationship to companies
    companies = relationship("Company", back_populates="status")

# Setup database tables
async def setup_db():
    try:
        async with engine.begin() as conn:
            # Create the schema if it doesn't exist
            if DATABASE_SCHEMA:
                await conn.execute(CreateSchema(DATABASE_SCHEMA, if_not_exists=True))
                logger.info(f"Schema '{DATABASE_SCHEMA}' ensured for company table.")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database setup complete.")
    except Exception as e:
        logger.error(f"Failed to setup database: {str(e)}")
        raise

# Get a database session
async def get_db_session():
    try:
        logger.debug("Creating a new database session...")
        async with async_session() as session:
            yield session
        logger.debug("Database session closed successfully.")
    except Exception as e:
        logger.error("Failed to get database session: {}", str(e))
        raise