#!/usr/bin/env python3
"""
FORMAP AI Assistant - Form Filler with LLM

This script uses an LLM to intelligently fill form fields based on a mapping file and input data.
"""

import json
import argparse
import openai
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure your OpenAI API key here
# openai.api_key = 'your-api-key-here'

def load_json_file(file_path: str) -> Dict:
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_field_info(field: Dict) -> str:
    """Extract relevant information from a form field mapping."""
    info = []
    if field.get('name'):
        info.append(f"name: {field['name']}")
    if field.get('label'):
        info.append(f"label: {field['label']}")
    if field.get('type'):
        info.append(f"type: {field['type']}")
    if field.get('xpath'):
        info.append(f"xpath: {field['xpath']}")
    return ", ".join(info)

def generate_llm_prompt(fields: List[Dict], form_data: Dict) -> str:
    """Generate a prompt for the LLM to map form fields to data."""
    fields_info = "\n".join([f"- {i+1}. {extract_field_info(field)}" for i, field in enumerate(fields)])
    
    prompt = f"""You are an AI assistant that helps fill out web forms. Your task is to map the form fields to the provided data.

AVAILABLE FORM FIELDS:
{fields_info}

AVAILABLE DATA:
{form_data}

For each form field, provide the most appropriate value from the available data. If no good match is found, use null.

Return a JSON object with field xpaths as keys and the corresponding values. Only include fields that should be filled.

Example output:
{{
  "//input[@id='first_name']": "John",
  "//input[@id='last_name']": "Doe"
}}

MAPPING:
"""
    return prompt

def get_llm_mapping(prompt: str) -> Dict[str, Any]:
    """Get field mapping from LLM."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that maps form fields to data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the JSON from the response
        result = response.choices[0].message.content.strip()
        # Sometimes the response includes markdown code blocks
        if '```json' in result:
            result = result.split('```json')[1].split('```')[0].strip()
        elif '```' in result:
            result = result.split('```')[1].split('```')[0].strip()
            
        return json.loads(result)
    except Exception as e:
        print(f"Error getting LLM mapping: {e}")
        return {}

def fill_form_with_mapping(mapping_file: str, data_file: str, output_file: Optional[str] = None):
    """Fill a form using LLM to map fields to data."""
    # Load the form mapping and data
    form_mapping = load_json_file(mapping_file)
    form_data = load_json_file(data_file)
    
    # Generate a prompt for the LLM
    prompt = generate_llm_prompt(form_mapping['fields'], form_data)
    print("\nGenerating field mapping with LLM...")
    
    # Get the field mapping from LLM
    field_mapping = get_llm_mapping(prompt)
    
    if not field_mapping:
        print("Failed to generate field mapping.")
        return
    
    # Create a mapping of xpath to field info for lookup
    xpath_to_field = {field['xpath']: field for field in form_mapping['fields']}
    
    # Prepare the filled form data
    filled_form = {
        'url': form_mapping['url'],
        'fields': []
    }
    
    # Create the filled form data structure
    for xpath, value in field_mapping.items():
        if xpath in xpath_to_field:
            field = xpath_to_field[xpath].copy()
            field['value'] = value
            filled_form['fields'].append(field)
    
    # Save the filled form data
    output_path = output_file or 'filled_form.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filled_form, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Filled form saved to {output_path}")
    print("\nYou can now use fill_form.py to submit the form:")
    print(f"python form-mapper/fill_form.py {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Fill a form using LLM to map fields to data.')
    parser.add_argument('mapping_file', help='Path to the form mapping JSON file')
    parser.add_argument('data_file', help='Path to the data JSON file')
    parser.add_argument('-o', '--output', help='Output file path (default: filled_form.json)')
    
    args = parser.parse_args()
    
    fill_form_with_mapping(args.mapping_file, args.data_file, args.output)

if __name__ == "__main__":
    main()
