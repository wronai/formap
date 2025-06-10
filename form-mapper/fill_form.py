#!/usr/bin/env python3
"""
Automatically fill a web form using a previously created field mapping.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

class FormFiller:
    def __init__(self, mapping_file: str = "form_map.json"):
        """Initialize the form filler with a field mapping file."""
        self.mapping_file = mapping_file
        self.mapping: Dict[str, Any] = {}
        self.field_data: Dict[str, Any] = {}
    
    def load_mapping(self) -> bool:
        """Load the field mapping from the JSON file."""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
            return True
        except FileNotFoundError:
            print(f"❌ Error: Mapping file '{self.mapping_file}' not found.")
            print("Please run 'python map_fields.py <url>' first to create the mapping.")
            return False
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in mapping file '{self.mapping_file}'")
            return False
    
    def get_field_data(self) -> bool:
        """Get field data from environment variables or user input."""
        print("\n📝 Enter values for each form field (press Enter to skip):")
        
        if not self.mapping.get('fields'):
            print("❌ No fields found in the mapping file.")
            return False
        
        for field in self.mapping['fields']:
            field_name = field.get('label') or field.get('name') or field['xpath']
            field_type = field.get('type', 'text')
            
            # Skip buttons and submit inputs
            if field_type in ['button', 'submit', 'reset']:
                continue
            
            # Get value from environment variable or prompt user
            env_var = f"FORM_{field.get('name', '').upper()}" if field.get('name') else None
            if env_var and env_var in os.environ:
                value = os.environ[env_var]
                print(f"Using value from environment for {field_name}: {value}")
            else:
                value = input(f"{field_name} ({field_type}): ").strip()
            
            if value:
                self.field_data[field['xpath']] = {
                    'value': value,
                    'type': field_type
                }
        
        return bool(self.field_data)
    
    async def fill_form(self):
        """Fill the form using the loaded mapping and field data."""
        if not self.mapping.get('url'):
            print("❌ No URL found in the mapping file.")
            return
        
        print(f"\n🌐 Opening {self.mapping['url']}...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to the URL
                await page.goto(self.mapping['url'], wait_until="domcontentloaded")
                await page.wait_for_load_state("networkidle")
                
                # Fill each field
                filled_count = 0
                for xpath, data in self.field_data.items():
                    try:
                        element = await page.wait_for_selector(f"xpath={xpath}", timeout=5000)
                        
                        # Handle different field types
                        field_type = data['type'].lower()
                        value = data['value']
                        
                        if field_type in ['select-one', 'select-multiple']:
                            await element.select_option(value)
                        elif field_type == 'checkbox':
                            if value.lower() in ['true', 'yes', '1', 'on']:
                                await element.check()
                            else:
                                await element.uncheck()
                        elif field_type == 'radio':
                            await element.check()
                        else:
                            await element.fill(value)
                        
                        print(f"✅ Filled: {xpath} = {value}")
                        filled_count += 1
                        
                        # Small delay between fields for better reliability
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"❌ Failed to fill {xpath}: {str(e)}")
                
                print(f"\n✅ Successfully filled {filled_count} out of {len(self.field_data)} fields.")
                print("\nPress Enter to close the browser...")
                input()
                
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                
            finally:
                await browser.close()

def main():
    """Main function to run the form filler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatically fill a web form using a field mapping.')
    parser.add_argument('mapping_file', nargs='?', default='form_map.json',
                       help='Path to the JSON file containing the form field mapping')
    args = parser.parse_args()
    
    filler = FormFiller(args.mapping_file)
    
    if not filler.load_mapping():
        return
    
    if not filler.get_field_data():
        print("\n❌ No field data provided. Exiting.")
        return
    
    asyncio.run(filler.fill_form())

if __name__ == "__main__":
    main()
