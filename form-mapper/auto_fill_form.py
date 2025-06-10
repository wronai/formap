#!/usr/bin/env python3
"""
Auto Form Filler - Automatically fills forms and handles file uploads
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from playwright.async_api import async_playwright

class AutoFormFiller:
    def __init__(self, url: str, data_file: str = "form_data.json", 
                 mapping_file: str = "form_map_auto.json", 
                 upload_dir: str = "~/uploads"):
        self.url = url
        self.data_file = data_file
        self.mapping_file = mapping_file
        self.upload_dir = os.path.expanduser(upload_dir)
        self.page = None
        self.browser = None
        self.playwright = None
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)

    async def setup(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})

    async def load_data(self) -> Dict:
        """Load form data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data file: {e}")
            return {}

    async def load_mapping(self) -> Dict:
        """Load field mapping from JSON file."""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading mapping file: {e}")
            return []

    def find_upload_file(self, field_name: str) -> Optional[str]:
        """Find a file to upload based on field name."""
        # Common file patterns to look for
        patterns = [
            f"{field_name}.*",
            "cv.*", "lebenslauf.*", "resume.*",
            "*.pdf", "*.doc", "*.docx"
        ]
        
        for pattern in patterns:
            for ext in ['', '.pdf', '.doc', '.docx']:
                full_pattern = f"{pattern}{ext}"
                for file in Path(self.upload_dir).glob(full_pattern.lower()):
                    return str(file)
                for file in Path(self.upload_dir).glob(full_pattern.upper()):
                    return str(file)
        return None

    async def fill_form(self):
        """Fill the form automatically based on mapping and data."""
        print(f"\n🔍 Opening {self.url}...")
        await self.page.goto(self.url, wait_until="domcontentloaded")
        
        data = await self.load_data()
        if not data:
            print("❌ No form data found")
            return
            
        mapping = await self.load_mapping()
        if not mapping:
            print("❌ No field mapping found")
            return
        
        print("\n🔄 Filling form...")
        
        # Handle file chooser events
        async def handle_file_chooser(file_chooser):
            field_xpath = await self.page.evaluate('''() => {
                return document.activeElement.getAttribute('data-xpath');
            }''')
            
            if field_xpath:
                field = next((f for f in mapping if f.get('xpath') == field_xpath), None)
                if field:
                    file_path = self.find_upload_file(field.get('name', 'cv'))
                    if file_path:
                        try:
                            await file_chooser.set_files(file_path)
                            print(f"📤 Uploaded file: {file_path}")
                        except Exception as e:
                            print(f"❌ Error uploading file: {e}")
        
        self.page.on('filechooser', handle_file_chooser)
        
        # Fill each field in the mapping
        for field in mapping:
            xpath = field.get('xpath')
            field_type = field.get('type', '').lower()
            field_name = field.get('name', '').lower()
            
            try:
                element = await self.page.wait_for_selector(f'xpath={xpath}', timeout=5000)
                
                # Handle different field types
                if field_type == 'file':
                    print(f"📎 Found file upload field: {field_name}")
                    await element.click()
                    await asyncio.sleep(1)  # Wait for file chooser
                elif field_type in ['radio', 'checkbox']:
                    await element.check()
                else:
                    # Get value from data based on field name
                    value = self.get_nested_value(data, field_name) or ''
                    if value:
                        await element.fill(str(value))
                        print(f"✅ Filled {field_name}: {value}")
                
                # Move to next field
                await element.press('Tab')
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️  Could not fill field {field_name}: {e}")
        
        print("\n✅ Form filled successfully!")

    def get_nested_value(self, data, key_path):
        """Get value from nested dictionary using dot notation."""
        keys = key_path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                return None
        return value

    async def run(self):
        """Run the form filler."""
        try:
            await self.setup()
            await self.fill_form()
            
            # Keep browser open for a while
            print("\nForm filling complete. Press Ctrl+C to exit...")
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_fill_form.py <url> [data_file] [mapping_file] [upload_dir]")
        sys.exit(1)
        
    url = sys.argv[1]
    data_file = sys.argv[2] if len(sys.argv) > 2 else "form_data.json"
    mapping_file = sys.argv[3] if len(sys.argv) > 3 else "form_map.json"
    upload_dir = sys.argv[4] if len(sys.argv) > 4 else "~/uploads"
    
    filler = AutoFormFiller(url, data_file, mapping_file, upload_dir)
    asyncio.run(filler.run())
