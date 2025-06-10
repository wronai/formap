"""Form field models and types."""
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field


class FieldType(str, Enum):
    """Supported form field types."""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    TEL = "tel"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE = "file"
    HIDDEN = "hidden"
    SUBMIT = "submit"
    BUTTON = "button"
    UNKNOWN = "unknown"


@dataclass
class FieldOption:
    """Represents an option in a select or radio group."""
    value: str
    text: str
    selected: bool = False


@dataclass
class FormField:
    """Represents a form field with all its properties."""
    name: str
    field_type: FieldType
    xpath: str
    label: str = ""
    placeholder: str = ""
    value: str = ""
    required: bool = False
    disabled: bool = False
    read_only: bool = False
    multiple: bool = False
    accept: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    options: List[FieldOption] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["field_type"] = self.field_type.value
        data["options"] = [{"value": opt.value, "text": opt.text, "selected": opt.selected} 
                          for opt in self.options]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'FormField':
        """Create from dictionary."""
        if isinstance(data.get("field_type"), str):
            data["field_type"] = FieldType(data["field_type"])
        
        options_data = data.pop("options", [])
        options = [
            FieldOption(
                value=opt.get("value", ""),
                text=opt.get("text", ""),
                selected=opt.get("selected", False)
            )
            for opt in options_data
        ]
        
        # Handle legacy format where options might be a list of strings
        if isinstance(options_data, list) and options_data and not isinstance(options_data[0], dict):
            options = [FieldOption(value=opt, text=opt) for opt in options_data]
        
        return cls(options=options, **data)


class FormData(BaseModel):
    """Represents form data for filling."""
    fields: Dict[str, Any] = Field(default_factory=dict)
    files: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Get field value by name with dot notation support."""
        keys = field_name.split('.')
        value = self.fields
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def add_field(self, name: str, value: Any):
        """Add a field value with dot notation support."""
        keys = name.split('.')
        current = self.fields
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value

    def add_file(self, field_name: str, file_path: str):
        """Add a file path for a file upload field."""
        self.files[field_name] = file_path
