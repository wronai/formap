"""Utility functions for formap."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List

logger = logging.getLogger(__name__)

def load_json_file(file_path: Union[str, Path]) -> Any:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = Path(file_path).expanduser().resolve()
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save (must be JSON-serializable)
        file_path: Path where to save the JSON file
        indent: Number of spaces for indentation
        
    Raises:
        TypeError: If the data is not JSON-serializable
        OSError: If there's an error writing to the file
    """
    file_path = Path(file_path).expanduser().resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Path object for the directory
    """
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def normalize_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing extra whitespace.
    
    Args:
        text: The text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    return ' '.join(str(text).strip().split())

def get_nested_value(data: dict, key_path: str, default: Any = None) -> Any:
    """
    Get a value from a nested dictionary using dot notation.
    
    Args:
        data: The dictionary to search in
        key_path: Dot-separated path to the value (e.g., 'user.profile.name')
        default: Default value if key is not found
        
    Returns:
        The value if found, otherwise the default value
    """
    keys = key_path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value

def set_nested_value(data: dict, key_path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using dot notation.
    
    Args:
        data: The dictionary to update
        key_path: Dot-separated path to the value (e.g., 'user.profile.name')
        value: The value to set
    """
    keys = key_path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value

__all__ = [
    'load_json_file',
    'save_json_file',
    'ensure_directory',
    'is_valid_url',
    'normalize_text',
    'get_nested_value',
    'set_nested_value',
]
