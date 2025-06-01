"""
Logging configuration for DevMind Backend
"""
import logging
import logging.config
import sys
from pathlib import Path
from datetime import datetime

from config import settings

def setup_logging():
    """Setup logging configuration for DevMind"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"devmind_{timestamp}.log"
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": str(log_file),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler", 
                "formatter": "detailed",
                "filename": str(log_dir / f"devmind_errors_{timestamp}.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 3
            }
        },
        "root": {
            "level": "DEBUG" if settings.debug else "INFO",
            "handlers": ["console", "file", "error_file"]
        },
        "loggers": {
            "devmind": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "mcp": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Create application logger
    logger = logging.getLogger("devmind")
    
    # Log startup message
    logger.info("🚀 DevMind logging system initialized")
    logger.info(f"📁 Log files location: {log_dir.absolute()}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f"devmind.{name}")

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)

# Custom log formatter for development
class ColoredFormatter(logging.Formatter):
    """Colored log formatter for better console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_colored_logging():
    """Setup colored logging for development"""
    if settings.debug:
        # Create colored console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Use colored formatter
        colored_formatter = ColoredFormatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(colored_formatter)
        
        # Get root logger and add colored handler
        root_logger = logging.getLogger()
        
        # Remove existing console handlers
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                root_logger.removeHandler(handler)
        
        root_logger.addHandler(console_handler)

# Context managers for temporary log level changes
class LogLevel:
    """Context manager for temporarily changing log level"""
    
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.original_level = logger.level
    
    def __enter__(self):
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)

# Utility functions for structured logging
def log_api_request(logger: logging.Logger, method: str, endpoint: str, user_id: str = None):
    """Log API request in structured format"""
    logger.info(
        "API Request",
        extra={
            "method": method,
            "endpoint": endpoint,
            "user_id": user_id,
            "type": "api_request"
        }
    )

def log_mcp_operation(logger: logging.Logger, operation: str, tool: str, success: bool, duration: float):
    """Log MCP operation in structured format"""
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"MCP Operation: {operation}",
        extra={
            "operation": operation,
            "tool": tool,
            "success": success,
            "duration": duration,
            "type": "mcp_operation"
        }
    )

def log_integration_sync(logger: logging.Logger, integration: str, status: str, items_processed: int = None):
    """Log integration sync in structured format"""
    logger.info(
        f"Integration Sync: {integration}",
        extra={
            "integration": integration,
            "status": status,
            "items_processed": items_processed,
            "type": "integration_sync"
        }
    )

# Performance logging decorator
def log_execution_time(logger: logging.Logger = None):
    """Decorator to log function execution time"""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                (logger or logging.getLogger()).info(
                    f"Function {func.__name__} completed in {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                (logger or logging.getLogger()).error(
                    f"Function {func.__name__} failed after {duration:.3f}s: {e}"
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                (logger or logging.getLogger()).info(
                    f"Function {func.__name__} completed in {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                (logger or logging.getLogger()).error(
                    f"Function {func.__name__} failed after {duration:.3f}s: {e}"
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator