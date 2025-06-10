"""Formap - Advanced Form Mapper & Auto-Filler."""

__version__ = "0.1.0"

from .form_detector import FormDetector, FormField, FieldType
from .logger import log, setup_logger

__all__ = [
    'FormDetector',
    'FormField',
    'FieldType',
    'log',
    'setup_logger',
]
