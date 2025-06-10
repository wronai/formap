#!/usr/bin/env python3
"""
Auto Form Mapper - Automatically maps form fields without user interaction
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from playwright.async_api import async_playwright

class AutoFormMapper:
    def __init__(self, url: str, output_file: str = "form_map_auto.json"):
        self.url = url
        self.output_file = output_file
        self.fields: List[Dict] = []
        self.browser = None
        self.page = None
        self.playwright = None

    async def setup(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})

    async def detect_form_fields(self):
        """Detect all form fields on the page."""
        print(f"🔍 Detecting form fields on {self.url}...")
        
        # Make sure we're on the page
        await self.page.goto(self.url, wait_until="domcontentloaded")
        
        # Inject JavaScript to find all form elements
        self.fields = await self.page.evaluate("""() => {
            const fields = [];
            
            // Common form elements
            const formElements = Array.from(document.querySelectorAll(
                'input:not([type="hidden"]):not([type="submit"]):not([type="button"]), ' +
                'select, textarea, [role="textbox"], [contenteditable="true"]'
            ));
            
            // Also look for file inputs that might be hidden
            const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
            
            // Combine and deduplicate
            const allElements = [...new Set([...formElements, ...fileInputs])];
            
            for (const element of allElements) {
                try {
                    // Skip if not visible
                    const style = window.getComputedStyle(element);
                    if (style.display === 'none' || style.visibility === 'hidden' || 
                        style.opacity === '0' || style.width === '0px' || 
                        style.height === '0px' || element.offsetParent === null) {
                        continue;
                    }
                    
                    // Get element properties
                    const tag = element.tagName.toLowerCase();
                    const type = element.type || tag;
                    const id = element.id || '';
                    const name = element.name || '';
                    const value = element.value || '';
                    const placeholder = element.placeholder || '';
                    const required = element.required || false;
                    const disabled = element.disabled || false;
                    const readOnly = element.readOnly || false;
                    const multiple = element.multiple || false;
                    const accept = element.accept || '';
                    
                    // Get label
                    let label = '';
                    if (element.labels && element.labels.length > 0) {
                        label = Array.from(element.labels)
                            .map(l => l.textContent.trim())
                            .filter(Boolean)
                            .join(' ');
                    } else if (element.id) {
                        const labelElement = document.querySelector(`label[for="${element.id}"]`);
                        if (labelElement) {
                            label = labelElement.textContent.trim();
                        }
                    }
                    
                    // Get XPath
                    const getXPath = (element) => {
                        if (element.id) return `//*[@id="${element.id}"]`;
                        if (element === document.body) return '/html/body';
                        
                        const parts = [];
                        let current = element;
                        
                        while (current && current.nodeType === 1) {
                            let index = 0;
                            let hasFollowingSiblings = false;
                            
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
                            
                            let part = '';
                            if (idPart) {
                                part = `//${tagName}${idPart}`;
                                parts.unshift(part);
                                break;
                            } else if (hasFollowingSiblings) {
                                part = `/${tagName}[${index + 1}]`;
                            } else {
                                part = `/${tagName}`;
                            }
                            
                            parts.unshift(part);
                            current = current.parentNode;
                        }
                        
                        return parts.join('');
                    };
                    
                    const xpath = getXPath(element);
                    
                    fields.push({
                        xpath,
                        tag,
                        type: type.toLowerCase(),
                        name,
                        id,
                        label,
                        value,
                        placeholder,
                        required,
                        disabled,
                        readOnly,
                        multiple,
                        accept,
                        isFileInput: type.toLowerCase() === 'file'
                    });
                    
                } catch (e) {
                    console.error('Error processing element:', e);
                }
            }
            
            return fields;
        }""")
        
        print(f"✅ Found {len(self.fields)} form fields")

    async def save_mapping(self):
        """Save the field mapping to a JSON file."""
        if not self.fields:
            print("⚠️  No fields to save")
            return
            
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.fields, f, indent=2, ensure_ascii=False)
            print(f"✅ Mapping saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving mapping: {e}")
            return False

    async def run(self):
        """Run the form mapper."""
        try:
            await self.setup()
            await self.detect_form_fields()
            await self.save_mapping()
            print("✅ Done!")
                
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
        print("Usage: python auto_map_form.py <url> [output_file]")
        sys.exit(1)
        
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "form_map_auto.json"
    
    mapper = AutoFormMapper(url, output_file)
    asyncio.run(mapper.run())
