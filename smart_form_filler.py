#!/usr/bin/env python3
"""
Smart Form Filler - Fills forms using field mapping and data files
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

def load_json_file(file_path: str) -> Dict:
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_matching_value(field: Dict, data: Dict) -> Any:
    """Find the best matching value for a field from the data."""
    field_name = field.get('name', '').lower()
    field_label = field.get('label', '').lower()
    
    # Common field mappings
    field_mappings = {
        'salutation': ['anrede', 'title', 'titel'],
        'first_name': ['vorname', 'name', 'imie'],
        'last_name': ['nachname', 'surname', 'nazwisko'],
        'email': ['e-mail', 'mail', 'email'],
        'phone': ['telefon', 'phone', 'telephone', 'tel'],
        'address': ['adresse', 'street', 'ulica'],
        'city': ['ort', 'miasto'],
        'zip': ['plz', 'postleitzahl', 'kod']
    }
    
    # Check direct matches first
    for key, aliases in field_mappings.items():
        if (field_name == key or 
            any(alias in field_name for alias in aliases) or
            any(alias in field_label for alias in aliases)):
            
            # Try to find the value in the data
            if key in data:
                return data[key]
            
            # Try nested structures
            if 'personal_info' in data and key in data['personal_info']:
                return data['personal_info'][key]
    
    # Try to find by field name in nested structures
    if 'personal_info' in data and field_name in data['personal_info']:
        return data['personal_info'][field_name]
    
    # Try to find by partial match in field names
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if field_name in subkey or field_name in field_label:
                    return subvalue
    
    return None

def fill_form(mapping_file: str, data_file: str, output_file: Optional[str] = None):
    """Fill a form using field mapping and data."""
    # Load the form mapping and data
    form_mapping = load_json_file(mapping_file)
    form_data = load_json_file(data_file)
    
    # Prepare the filled form data
    filled_form = {
        'url': form_mapping['url'],
        'fields': []
    }
    
    # Fill each field
    for field in form_mapping['fields']:
        field_copy = field.copy()
        value = find_matching_value(field, form_data)
        
        if value is not None:
            field_copy['value'] = value
            filled_form['fields'].append(field_copy)
    
    # Save the filled form data
    output_path = output_file or 'filled_form.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filled_form, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Filled form saved to {output_path}")
    print("\nYou can now use fill_form.py to submit the form:")
    print(f"python form-mapper/fill_form.py {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Fill a form using field mapping and data files.')
    parser.add_argument('mapping_file', help='Path to the form mapping JSON file')
    parser.add_argument('data_file', help='Path to the data JSON file')
    parser.add_argument('-o', '--output', help='Output file path (default: filled_form.json)')
    
    args = parser.parse_args()
    
    fill_form(args.mapping_file, args.data_file, args.output)

if __name__ == "__main__":
    main()
