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
                 upload_dir: str = "~/uploads",
                 headless: bool = False):
        self.url = url
        self.data_file = data_file
        self.mapping_file = mapping_file
        self.upload_dir = os.path.expanduser(upload_dir)
        self.headless = headless
        self.page = None
        self.browser = None
        self.playwright = None
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        print(f"📁 Using upload directory: {self.upload_dir}")
        
        # List available upload files
        uploads = list(Path(self.upload_dir).glob('*'))
        if uploads:
            print("📋 Available upload files:")
            for file in uploads:
                print(f"   - {file.name}")
        else:
            print("⚠️  No files found in upload directory")

    async def setup(self):
        """Initialize browser and page."""
        print("🚀 Launching browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )
        context = await self.browser.new_context(no_viewport=True)
        self.page = await context.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})
        
        # Handle dialogs
        self.page.on('dialog', lambda dialog: dialog.accept())

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
            f"*{field_name}*",
            "*cv*", "*lebenslauf*", "*resume*",
            "*bewerbung*", "*application*",
            "*.pdf", "*.doc", "*.docx"
        ]
        
        # Try exact matches first
        for ext in ['', '.pdf', '.doc', '.docx']:
            exact_path = Path(self.upload_dir) / f"{field_name}{ext}"
            if exact_path.exists():
                return str(exact_path)
        
        # Try pattern matching
        for pattern in patterns:
            for ext in ['', '.pdf', '.doc', '.docx']:
                full_pattern = f"{pattern}{ext}"
                matches = list(Path(self.upload_dir).glob(full_pattern.lower()))
                if matches:
                    return str(matches[0])
                matches = list(Path(self.upload_dir).glob(full_pattern.upper()))
                if matches:
                    return str(matches[0])
        
        # If nothing found, return first available file
        all_files = list(Path(self.upload_dir).glob('*'))
        if all_files:
            print(f"⚠️  No specific match for '{field_name}'. Using first available file: {all_files[0].name}")
            return str(all_files[0])
            
        return None

    async def fill_form(self):
        """Fill the form automatically based on mapping and data."""
        print(f"\n🔍 Opening {self.url}...")
        await self.page.goto(self.url, wait_until="networkidle")
        
        # Handle cookie consent if present
        cookie_selectors = [
            'button#onetrust-accept-btn-handler',
            'button[aria-label*="cookie" i], button[class*="cookie" i]',
            'button:has-text("Accept")',
            'button:has-text("Akzeptieren")',
            'button:has-text("Zustimmen")'
        ]
        
        for selector in cookie_selectors:
            try:
                await self.page.click(selector, timeout=1000)
                print(f"✅ Clicked cookie button: {selector}")
                await asyncio.sleep(1)
                break
            except Exception:
                continue
        
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
                    field_name = field.get('name', 'cv').lower()
                    file_path = self.find_upload_file(field_name)
                    if file_path:
                        try:
                            await file_chooser.set_files(file_path)
                            print(f"📤 Uploaded file: {file_path}")
                            # Wait for upload to complete
                            await asyncio.sleep(2)
                        except Exception as e:
                            print(f"❌ Error uploading file: {e}")
        
        self.page.on('filechooser', handle_file_chooser)
        
        # First pass: Handle all non-file fields
        for field in mapping:
            xpath = field.get('xpath')
            field_type = field.get('type', '').lower()
            field_name = field.get('name', '').lower()
            
            # Skip file uploads in first pass
            if field_type == 'file':
                continue
                
            try:
                element = await self.page.wait_for_selector(f'xpath={xpath}', timeout=3000, state='attached')
                
                # Skip hidden elements
                is_visible = await element.is_visible()
                if not is_visible:
                    print(f"⚠️  Skipping hidden field: {field_name}")
                    continue
                
                # Scroll element into view
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(0.2)
                
                # Handle different field types
                if field_type in ['radio', 'checkbox']:
                    await element.check()
                    print(f"✅ Checked {field_name}")
                else:
                    # Get value from data based on field name
                    value = self.get_nested_value(data, field_name) or ''
                    if value:
                        await element.click()  # Focus the field
                        await asyncio.sleep(0.2)
                        await element.fill('')  # Clear existing value
                        await element.type(str(value), delay=50)  # Type with delay
                        print(f"✅ Filled {field_name}: {value}")
                
                # Move to next field
                await element.press('Tab')
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"⚠️  Could not fill field {field_name}: {e}")
        
        # Second pass: Handle file uploads
        print("\n📎 Handling file uploads...")
        for field in mapping:
            xpath = field.get('xpath')
            field_type = field.get('type', '').lower()
            field_name = field.get('name', '').lower()
            
            if field_type != 'file':
                continue
                
            try:
                element = await self.page.wait_for_selector(f'xpath={xpath}', timeout=5000, state='attached')
                await element.scroll_into_view_if_needed()
                
                # Set data-xpath attribute for the file chooser handler
                await self.page.evaluate('''(element, xpath) => {
                    element.setAttribute('data-xpath', xpath);
                }''', element, xpath)
                
                print(f"📤 Preparing to upload file for: {field_name}")
                
                # Click the file input to trigger the file chooser
                await element.click()
                await asyncio.sleep(2)  # Wait for file chooser
                
            except Exception as e:
                print(f"⚠️  Could not handle file upload for {field_name}: {e}")
        
        # Handle form submission if there's a submit button
        try:
            print("\n🚀 Submitting form...")
            # Try to find and click the submit button
            submit_buttons = await self.page.query_selector_all('button[type="submit"], input[type="submit"]')
            if submit_buttons:
                await submit_buttons[0].click()
                print("✅ Form submitted successfully!")
                await asyncio.sleep(3)  # Wait for submission to complete
            else:
                print("⚠️  No submit button found. Form not submitted.")
        except Exception as e:
            print(f"⚠️  Error submitting form: {e}")
        
        print("\n✅ Form filling process completed!")

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
            
            if not self.headless:
                # Keep browser open if not in headless mode
                print("\n✅ Form filling complete. Browser will remain open...")
                print("   Press Ctrl+C to exit when done reviewing.")
                while True:
                    await asyncio.sleep(1)
            else:
                print("\n✅ Form filling complete in headless mode.")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if not self.headless:
                print("\nBrowser will remain open for debugging. Press Ctrl+C to exit.")
                while True:
                    await asyncio.sleep(1)
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatically fill web forms with data from JSON files.')
    parser.add_argument('url', help='URL of the form to fill')
    parser.add_argument('-d', '--data', default='form_data.json',
                      help='Path to JSON file containing form data (default: form_data.json)')
    parser.add_argument('-m', '--mapping', default='form_map_auto.json',
                      help='Path to JSON file containing form field mappings (default: form_map_auto.json)')
    parser.add_argument('-u', '--upload-dir', default='~/uploads',
                      help='Directory containing files to upload (default: ~/uploads)')
    parser.add_argument('--headless', action='store_true',
                      help='Run in headless mode (no browser UI)')
    
    args = parser.parse_args()
    
    print(f"\n🚀 Starting form filler with the following settings:")
    print(f"   URL: {args.url}")
    print(f"   Data file: {args.data}")
    print(f"   Mapping file: {args.mapping}")
    print(f"   Upload directory: {args.upload_dir}")
    print(f"   Headless mode: {'Yes' if args.headless else 'No'}")
    
    filler = AutoFormFiller(
        url=args.url,
        data_file=args.data,
        mapping_file=args.mapping,
        upload_dir=args.upload_dir,
        headless=args.headless
    )
    
    asyncio.run(filler.run())
