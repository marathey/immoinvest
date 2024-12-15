import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON, TIMESTAMP, text, UUID, MetaData, Integer
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
            "application_name": "audit-log-service"  # Helps with debugging
        }
    }
)

logger.info("Database engine created with URL: {}", DATABASE_URL)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": DATABASE_SCHEMA} if DATABASE_SCHEMA else None  # Explicit schema binding
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Use uuid.uuid4
    timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    service_name = Column(String(255), nullable=False)
    service_id = Column(String(255), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action_type = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    previous_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    

# Setup database tables
async def setup_db():
    try:
        async with engine.begin() as conn:
            # Create the schema if it doesn't exist
            if DATABASE_SCHEMA:
                await conn.execute(CreateSchema(DATABASE_SCHEMA, if_not_exists=True))
                logger.info(f"Schema '{DATABASE_SCHEMA}' ensured for audit_logs table.")
            
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