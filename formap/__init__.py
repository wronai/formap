"""Formap - Advanced Form Mapper & Auto-Filler."""

__version__ = "0.2.0"

# Core models
from .models.field import (
    FormField,
    FormData,
    FieldType,
    FieldOption,
)

# Services
from .services import (
    FormDetector,
    DetectionOptions,
    FormFiller,
)

# Utils
from .utils import (
    load_json_file,
    save_json_file,
    ensure_directory,
    is_valid_url,
    normalize_text,
    get_nested_value,
    set_nested_value,
)

# Logging
from .logger import log, setup_logger

__all__ = [
    # Core models
    'FormField',
    'FormData',
    'FieldType',
    'FieldOption',
    
    # Services
    'FormDetector',
    'DetectionOptions',
    'FormFiller',
    
    # Utils
    'load_json_file',
    'save_json_file',
    'ensure_directory',
    'is_valid_url',
    'normalize_text',
    'get_nested_value',
    'set_nested_value',
    
    # Logging
    'log',
    'setup_logger',
]
