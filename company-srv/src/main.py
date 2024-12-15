import uvicorn
import sys
import os
import logging
from pathlib import Path
from loguru import logger
from app.api import app
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))

load_dotenv()

# Default values
DEFAULT_LOG_FILE_STORAGE = "/var/log/audit_log_srv.log"
DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_ROTATION = "10 MB"
DEFAULT_LOG_RETENTION = "7 days"

# Get values from .env or use defaults
LOG_FILE_STORAGE = os.getenv("LOG_FILE_STORAGE", DEFAULT_LOG_FILE_STORAGE)
LOG_LEVEL = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
LOG_ROTATION = os.getenv("LOG_ROTATION", DEFAULT_LOG_ROTATION)
LOG_RETENTION = os.getenv("LOG_RETENTION", DEFAULT_LOG_RETENTION)


# Intercept standard logging to route it through Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Map Python logging levels to Loguru levels
        try:
            log_level = logger.level(record.levelname).name
        except KeyError:
            log_level = record.levelno  # Fallback to record's numeric level

        # Log the message using Loguru
        logger.log(log_level, record.getMessage())


# Configure Loguru for JSON logging
def configure_logger():
    logger.remove()  # Remove default Loguru handlers

    # Add JSON log handler for stdout
    logger.add(
        sys.stdout,
        serialize=True,  # Output logs in JSON format
        level="DEBUG",   # Adjust based on your environment
        enqueue=True,    # Thread-safe logging
    )
    # File logging (Promtail scrapes this file)
    logger.add(
        LOG_FILE_STORAGE,  # Log file path inside Docker container
        format="{message}",
        serialize=True,  # Write logs in JSON format
        level=LOG_LEVEL,   # Adjust the level as needed
        rotation=LOG_ROTATION,  # Rotate logs after 10 MB
        retention=LOG_RETENTION  # Retain logs for 7 days
    )

    # Log each configuration individually
    logger.info(f"Logger configuration: LOG_FILE_STORAGE={LOG_FILE_STORAGE}")
    logger.info(f"Logger configuration: LOG_LEVEL={LOG_LEVEL}")
    logger.info(f"Logger configuration: LOG_ROTATION={LOG_ROTATION}")
    logger.info(f"Logger configuration: LOG_RETENTION={LOG_RETENTION}")
    logger.info(f"Logger configuration: DATABASE_URL={os.getenv("DATABASE_URL")}")

    # Intercept Uvicorn and other library logs
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

# Initialize logging
configure_logger()

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_config=None # Default uvicorn log disabled as using logger
    )