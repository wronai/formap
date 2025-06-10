#!/usr/bin/env python3
"""
Form Field Mapper - Focused Version

This script maps only form fields by tabbing through them, ignoring navigation and other non-form elements.
"""

import asyncio
import json
from typing import Dict, List, Optional, Set
from playwright.async_api import async_playwright

class FormFieldMapper:
    def __init__(self, url: str, output_file: str = "form_map.json"):
        self.url = url
        self.output_file = output_file
        self.fields: List[Dict] = []
        self.mapped_xpaths: Set[str] = set()
        self.browser = None
        self.page = None
        self.playwright = None
        self.form_started = False

    async def setup(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        
        # Set viewport size for consistent behavior
        await self.page.set_viewport_size({"width": 1280, "height": 800})
        
        # Add JavaScript helpers
        await self.page.add_init_script("""
        // Helper to check if element is a form field
        window.isFormField = function(element) {
            if (!element || !element.tagName) return false;
            
            const tag = element.tagName.toLowerCase();
            const type = (element.type || '').toLowerCase();
            const role = (element.getAttribute('role') || '').toLowerCase();
            const style = window.getComputedStyle(element);
            
            // Skip non-interactive elements
            if (['script', 'style', 'svg', 'path', 'img', 'image', 'link'].includes(tag)) {
                return false;
            }
            
            // Skip hidden elements
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0' || 
                style.width === '0px' || style.height === '0px' || element.offsetParent === null) {
                return false;
            }
            
            // Check for file inputs first (including hidden ones)
            if (tag === 'input' && type === 'file') {
                return 'file';
            }
            
            // Standard form elements
            if (['input', 'textarea', 'select', 'button'].includes(tag)) {
                // Skip non-interactive inputs
                if (tag === 'input' && ['hidden', 'button', 'image', 'reset', 'submit'].includes(type)) {
                    return false;
                }
                // Skip disabled elements
                if (element.disabled) return false;
                return true;
            }
            
            // Content editable elements
            if (element.isContentEditable) return true;
            
            // ARIA form controls
            const formRoles = ['textbox', 'combobox', 'checkbox', 'radio', 'button', 'slider'];
            if (formRoles.includes(role)) return true;
            
            return false;
        };
        
        // Get XPath for an element
        window.getElementXPath = function(element) {
            if (!element || element.nodeType !== 1) return '';
            if (element.id) return `//*[@id="${element.id}"]`;
            if (element === document.body) return '/html/body';
            
            const parts = [];
            let current = element;
            
            while (current && current.nodeType === 1) {
                let index = 0;
                let hasFollowingSiblings = false;
                
                // Count previous siblings with the same tag name
                const siblings = current.parentNode ? 
                    Array.from(current.parentNode.children).filter(
                        el => el.tagName === current.tagName
                    ) : [];
                    
                if (siblings.length > 1) {
                    index = siblings.indexOf(current);
                    hasFollowingSiblings = true;
                }
                
                const tagName = current.tagName.toLowerCase();
                const idPart = current.id ? `[@id="${current.id}"]` : '';
                const classPart = current.className && typeof current.className === 'string' ? 
                    `[contains(concat(' ', normalize-space(@class), ' '), ' ${current.className.split(' ')[0]} ')]` : '';
                
                let part = '';
                if (idPart) {
                    part = `//${tagName}${idPart}`;
                    parts.unshift(part);
                    break;
                } else if (hasFollowingSiblings) {
                    part = `/${tagName}[${index + 1}]`;
                } else {
                    part = `/${tagName}${classPart || ''}`;
                }
                
                parts.unshift(part);
                current = current.parentNode;
            }
            
            return parts.join('');
        };
        
        // Get label for a form field
        window.getFieldLabel = function(element) {
            if (!element) return '';
            
            // Try to get associated label
            if (element.id) {
                const label = document.querySelector(`label[for="${element.id}"]`);
                if (label) return label.textContent.trim();
            }
            
            // Try to find parent label
            let parent = element.parentElement;
            while (parent && parent.tagName !== 'BODY') {
                if (parent.tagName === 'LABEL') {
                    return parent.textContent.trim();
                }
                parent = parent.parentElement;
            }
            
            // Try to find previous sibling text
            let prev = element.previousSibling;
            while (prev) {
                if (prev.nodeType === 3 && prev.textContent.trim()) {
                    return prev.textContent.trim();
                }
                prev = prev.previousSibling;
            }
            
            return '';
        };
        """)

    async def get_field_info(self) -> Optional[Dict]:
        """Get information about the currently focused field."""
        try:
            field_info = await self.page.evaluate("""() => {
                // Check currently focused element first
                let active = document.activeElement;
                let fieldType = window.isFormField(active);
                
                // If no active field, try to find first form field
                if (!fieldType) {
                    const allInputs = Array.from(document.querySelectorAll('input, textarea, select, button, [role="textbox"], [contenteditable="true"]'));
                    for (const el of allInputs) {
                        fieldType = window.isFormField(el);
                        if (fieldType) {
                            active = el;
                            active.focus();
                            break;
                        }
                    }
                }
                
                if (!active || !fieldType) return null;
                
                // Get field information
                const fieldInfo = {
                    xpath: window.getElementXPath(active),
                    tag: active.tagName.toLowerCase(),
                    type: active.type || active.tagName.toLowerCase(),
                    name: active.name || '',
                    id: active.id || '',
                    label: window.getFieldLabel(active),
                    placeholder: active.placeholder || '',
                    value: active.value || '',
                    accept: active.accept || '',
                    multiple: active.multiple || false,
                    isFileInput: fieldType === 'file'
                };
                
                return fieldInfo;
            }""")
            
            if not field_info:
                return None
                
            # Clean up the label
            if field_info.get('label'):
                field_info['label'] = ' '.join(str(field_info['label']).split())
                
            return field_info
            
        except Exception as e:
            print(f"Error getting field info: {e}")
            return None

    async def handle_file_upload(self, field_info: Dict):
        """Handle file upload for a file input field."""
        print("\n📎 File upload detected!")
        print(f"   Field: {field_info.get('label', 'Unnamed file input')}")
        print(f"   Accepts: {field_info.get('accept', 'Any file type')}")
        print(f"   Multiple: {'Yes' if field_info.get('multiple') else 'No'}")
        
        # You can modify this to use a specific file path or ask the user
        file_path = input("   Enter path to file to upload (or press Enter to skip): ").strip()
        
        if file_path and os.path.exists(file_path):
            field_info['file_path'] = file_path
            print(f"✅ Will upload: {file_path}")
        else:
            print("⚠️  No file selected or file not found")
            
        return field_info

    async def map_fields(self):
        """Map form fields by tabbing through them."""
        print(f"\n🔍 Opening {self.url} in browser...")
        await self.page.goto(self.url, wait_until="domcontentloaded")
        
        # Try to find file inputs that might be hidden or styled
        file_inputs = await self.page.query_selector_all('input[type="file"]')
        for file_input in file_inputs:
            try:
                # Make sure the input is visible
                await file_input.evaluate('el => el.style.display = "block"')
                await file_input.evaluate('el => el.style.visibility = "visible"')
                await file_input.evaluate('el => el.style.opacity = "1"')
                await file_input.evaluate('el => el.style.width = "auto"')
                await file_input.evaluate('el => el.style.height = "auto"')
                await file_input.evaluate('el => el.style.position = "static"')
            except:
                continue
        
        # Set up file chooser handling
        async def handle_file_chooser(file_chooser):
            field_xpath = await self.page.evaluate('''() => {
                const active = document.activeElement;
                return window.getElementXPath(active);
            }''')
            
            # Find the field in our mapped fields
            for field in self.fields:
                if field.get('xpath') == field_xpath and field.get('isFileInput'):
                    if 'file_path' in field:
                        await file_chooser.set_files(field['file_path'])
                        print(f"📤 Uploaded file: {field['file_path']}")
                    break
        
        # Listen for file chooser events
        self.page.on('filechooser', handle_file_chooser)
        
        print("\n📝 Tab through the form fields in the order you want them filled.")
        print("   Press 's' then Enter to save and exit.")
        print("   Press 'q' then Enter to quit without saving.\n")
        
        # Start tabbing through the form
        await self.page.keyboard.press("Tab")
        
        while True:
            # Get info about the current field
            field_info = await self.get_field_info()
            
            if field_info and field_info['xpath'] not in self.mapped_xpaths:
                # Handle file uploads
                if field_info.get('isFileInput'):
                    field_info = await self.handle_file_upload(field_info)
                
                self.fields.append(field_info)
                self.mapped_xpaths.add(field_info['xpath'])
                
                # Print field info
                label = field_info.get('label') or field_info.get('placeholder') or 'Unnamed field'
                print(f"✅ Mapped field: {label}")
                print(f"   Type: {field_info['type']}")
                print(f"   XPath: {field_info['xpath']}")
                if field_info.get('name'):
                    print(f"   Name: {field_info['name']}")
                print()
            
            # Wait for user input
            user_input = input("Press Enter to continue, 's' to save, or 'q' to quit: ").strip().lower()
            
            if user_input == 'q':
                print("\n❌ Mapping cancelled.")
                return False
            elif user_input == 's':
                return await self.save_mapping()
            
            # Move to the next field
            await self.page.keyboard.press("Tab")
            
            # Check if we've looped back to the beginning
            if await self.page.evaluate("document.activeElement === document.body"):
                print("\n⚠️  Reached the end of the form. Starting over...")
                await self.page.keyboard.press("Tab")

    async def save_mapping(self) -> bool:
        """Save the field mappings to a JSON file."""
        if not self.fields:
            print("❌ No form fields were mapped.")
            return False
            
        mapping = {
            'url': self.url,
            'fields': self.fields
        }
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Successfully mapped {len(self.fields)} fields to {self.output_file}")
            print("\nYou can now use fill_form.py to automatically fill this form:")
            print(f"python form-mapper/fill_form.py {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving mapping: {e}")
            return False

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Map form fields by tabbing through them.')
    parser.add_argument('url', help='URL of the webpage with the form')
    parser.add_argument('-o', '--output', default='form_map.json', 
                      help='Output JSON file (default: form_map.json)')
    args = parser.parse_args()
    
    mapper = FormFieldMapper(args.url, args.output)
    
    try:
        await mapper.setup()
        await mapper.map_fields()
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        await mapper.close()


if __name__ == "__main__":
    asyncio.run(main())
