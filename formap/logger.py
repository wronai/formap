import sys
from loguru import logger

def setup_logger(level: str = "INFO"):
    """Configure the logger with custom formatting and handlers."""
    logger.remove()  # Remove default handler
    
    # Add stderr handler with color
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    return logger

# Create a logger instance
log = setup_logger()
