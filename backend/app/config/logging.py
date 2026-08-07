from pathlib import Path

from loguru import logger

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Remove default console logger
logger.remove()

# Console Logger
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
)

# File Logger
logger.add(
    LOG_DIR / "backend.log",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
)

# Error Logger
logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
)