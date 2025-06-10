#!/usr/bin/env python3
"""
Map form fields by tabbing through them and save their XPaths to a JSON file.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Tuple

class FormField:
    def __init__(self, xpath: str, field_type: str, name: Optional[str] = None, label: Optional[str] = None):
        self.xpath = xpath
        self.type = field_type
        self.name = name
        self.label = label
    
    def to_dict(self) -> Dict:
        return {
            "xpath": self.xpath,
            "type": self.type,
            "name": self.name,
            "label": self.label
        }

async def get_active_element_info(page) -> Tuple[Optional[Dict], str]:
    """Get information about the currently focused element."""
    try:
        element = await page.evaluate('''() => {
            const active = document.activeElement;
            if (!active) return null;
            
            // Get XPath
            function getXPath(element) {
                if (!element) return '';
                if (element.id) return `//*[@id="${element.id}"]`;
                if (element === document.body) return '/html/body';
                
                let ix = 0;
                const siblings = element.parentNode ? element.parentNode.children : [];
                for (let i = 0; i < siblings.length; i++) {
                    const sibling = siblings[i];
                    if (sibling === element) {
                        return getXPath(element.parentNode) + 
                               '/' + 
                               element.tagName.toLowerCase() + 
                               (ix > 0 ? '[' + (ix + 1) + ']' : '');
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
                }
                return '';
            }
            
            const xpath = getXPath(active);
            
            // Get associated label
            let label = '';
            if (active.labels && active.labels.length > 0) {
                label = active.labels[0].textContent.trim();
            } else if (active.id && document.querySelector(`label[for="${active.id}"]`)) {
                label = document.querySelector(`label[for="${active.id}"]`).textContent.trim();
            } else {
                // Try to find a nearby label
                const parent = active.parentElement;
                if (parent) {
                    const labels = parent.getElementsByTagName('label');
                    if (labels.length > 0) {
                        label = labels[0].textContent.trim();
                    }
                }
            }
            
            return {
                xpath: xpath,
                type: active.type || active.tagName.toLowerCase(),
                name: active.name || '',
                value: active.value || '',
                label: label || ''
            };
        }''')
        
        if not element:
            return None, "No active element found"
            
        return element, ""
    except Exception as e:
        return None, f"Error getting active element: {str(e)}"

async def map_form_fields(url: str, output_json: str = "form_map.json"):
    """
    Map form fields on a webpage by tabbing through them.
    
    Args:
        url: The URL of the webpage with the form
        output_json: Path to save the form field mappings
    """
    print(f"\n🔍 Opening {url} in browser...")
    print("\n📝 Tab through the form fields in the order you want them filled.")
    print("   Press 's' then Enter to save and exit.")
    print("   Press 'q' then Enter to quit without saving.\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the URL
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for the page to load
            await page.wait_for_load_state("networkidle")
            
            fields = []
            field_xpaths = set()
            
            # Focus the first focusable element
            await page.keyboard.press("Tab")
            
            while True:
                # Get info about the currently focused element
                element_info, error = await get_active_element_info(page)
                
                if element_info:
                    xpath = element_info["xpath"]
                    
                    # Skip if we've already seen this field
                    if xpath in field_xpaths:
                        await page.keyboard.press("Tab")
                        continue
                        
                    field_type = element_info["type"]
                    field_name = element_info["name"]
                    field_label = element_info["label"]
                    
                    # Skip non-input elements
                    if field_type.lower() in ["button", "submit", "reset", "hidden"]:
                        await page.keyboard.press("Tab")
                        continue
                    
                    field = FormField(
                        xpath=xpath,
                        field_type=field_type,
                        name=field_name,
                        label=field_label
                    )
                    
                    fields.append(field)
                    field_xpaths.add(xpath)
                    
                    print(f"✅ Mapped field: {field_label or field_name or 'Unnamed field'}")
                    print(f"   Type: {field_type}")
                    print(f"   XPath: {xpath}\n")
                
                # Wait for user input
                user_input = input("Press Enter to continue, 's' to save, or 'q' to quit: ").strip().lower()
                
                if user_input == 's':
                    break
                elif user_input == 'q':
                    print("\n❌ Exiting without saving.")
                    return
                    
                # Move to the next focusable element
                await page.keyboard.press("Tab")
            
            # Save the mapped fields to a JSON file
            if fields:
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump({
                        "url": url,
                        "fields": [field.to_dict() for field in fields]
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"\n✅ Successfully mapped {len(fields)} fields to {output_json}")
                print("\nYou can now use fill_form.py to automatically fill this form.")
            else:
                print("\n❌ No fields were mapped.")
                
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "form_map.json"
        asyncio.run(map_form_fields(url, output_file))
    else:
        print("Usage: python map_fields.py <url> [output_file]")
        print("Example: python map_fields.py https://example.com/form form_map.json")
        print("\nPlease provide a URL to map the form fields.")
