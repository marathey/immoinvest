import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.schema import CreateSchema
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create Base class for models
Base = declarative_base()

# Create engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "server_settings": {
            "application_name": "company-service"
        }
    }
)

logger.info("Database engine created with URL: {}", DATABASE_URL)

# Create session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def setup_db():
    try:
        async with engine.begin() as conn:
            if DATABASE_SCHEMA:
                await conn.execute(CreateSchema(DATABASE_SCHEMA, if_not_exists=True))
                logger.info(f"Schema '{DATABASE_SCHEMA}' ensured for company table.")
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database setup complete.")
    except Exception as e:
        logger.error(f"Failed to setup database: {str(e)}")
        raise

async def get_db_session():
    try:
        logger.debug("Creating a new database session...")
        async with async_session() as session:
            yield session
        logger.debug("Database session closed successfully.")
    except Exception as e:
        logger.error("Failed to get database session: {}", str(e))
        raise