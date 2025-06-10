#!/usr/bin/env python3
"""
Auto Form Mapper - Automatically maps form fields without user interaction
"""

import asyncio
import json
import os
import re
import aiohttp
from typing import Dict, List, Optional, Any
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = None
        self.model = "mistral:7b"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using the local Ollama API."""
        url = urljoin(self.base_url, "/api/generate")
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "You are a helpful assistant that analyzes HTML form fields.",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "max_tokens": 200
            }
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get('response', '').strip()
        except Exception as e:
            print(f"⚠️  Ollama API error: {e}")
            return ""

class LLMFieldDetector:
    def __init__(self, ollama_url: str = None):
        """Initialize the LLM field detector with optional Ollama URL."""
        self.ollama_url = ollama_url or "http://localhost:11434"
        self.cache_file = Path("field_detection_cache.json")
        self.cache = self._load_cache()
        self.ollama = None
    
    def _load_cache(self) -> Dict:
        """Load cached field detections."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Save field detections to cache."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    async def detect_field_type(self, element_html: str, field_name: str = "") -> Dict[str, Any]:
        """Use local LLM to detect field type and properties."""
        # Check cache first
        cache_key = f"{field_name}:{hash(element_html)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Default response in case of errors
        default_response = {
            "type": "text", 
            "name": field_name, 
            "label": "", 
            "required": False, 
            "description": ""
        }
        
        # Initialize Ollama client if not already done
        if not self.ollama:
            self.ollama = OllamaClient(self.ollama_url)
        
        try:
            # Prepare the prompt for the LLM
            prompt = f"""Analyze this form field HTML and return a JSON object with these fields:
- type: input type (text, email, tel, file, checkbox, radio, select, etc.)
- name: field name if available
- label: field label if available
- required: boolean if field is required
- description: short description of what this field is for

HTML: {element_html}

Respond with ONLY the JSON object, no other text or formatting.
Example response: {{"type": "email", "name": "user_email", "label": "Email Address", "required": true, "description": "User's email address for account notifications"}}

JSON: """

            # Get response from local Ollama
            async with self.ollama as client:
                response = await client.generate(
                    prompt=prompt,
                    system_prompt="You are a helpful assistant that analyzes HTML form fields. Respond with only a valid JSON object, no other text or formatting."
                )
            
            # Clean up the response to extract just the JSON
            try:
                # Remove any text before the first {
                json_start = response.find('{')
                if json_start == -1:
                    return default_response
                    
                # Remove any text after the last }
                json_end = response.rfind('}') + 1
                if json_end <= 0:
                    return default_response
                    
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Ensure all required fields are present
                for key in ['type', 'name', 'label', 'required', 'description']:
                    if key not in result:
                        result[key] = default_response[key]
                
                # Cache the result
                self.cache[cache_key] = result
                self._save_cache()
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse LLM response: {e}")
                print(f"Raw response: {response}")
                return default_response
                
        except Exception as e:
            print(f"⚠️  LLM detection error: {e}")
            return default_response

class AutoFormMapper:
    def __init__(self, url: str, output_file: str = "form_map_auto.json", ollama_url: str = None, use_llm: bool = False):
        self.url = url
        self.output_file = output_file
        self.fields: List[Dict] = []
        self.browser = None
        self.page = None
        self.playwright = None
        # Initialize LLM detector only if explicitly requested
        self.llm_detector = LLMFieldDetector(ollama_url) if (ollama_url and use_llm) else None
        print(f"🔍 LLM analysis is {'enabled' if self.llm_detector else 'disabled'}")

    async def setup(self):
        """Initialize browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})

    async def get_element_html(self, element) -> str:
        """Get outer HTML of an element and its relevant context."""
        return await self.page.evaluate('''(element) => {
            // Get the element and its parent form if it exists
            const context = element.closest('form') || element.closest('div[class*="form"], section[class*="form"]') || element.parentElement;
            
            // Create a clean copy of the element and its context
            const clone = context.cloneNode(true);
            const elementInClone = clone.querySelector(`[id="${element.id}"]`) || 
                                Array.from(clone.querySelectorAll('*')).find(el => 
                                    el.outerHTML === element.outerHTML
                                );
            
            if (!elementInClone) return element.outerHTML;
            
            // Highlight the target element
            elementInClone.style.outline = '2px solid red';
            return clone.outerHTML;
        }''', element)

    async def detect_form_fields(self):
        """Detect all form fields on the page with better interaction."""
        print(f"🔍 Detecting form fields on {self.url}...")
        
        # Make sure we're on the page
        await self.page.goto(self.url, wait_until="networkidle")
        
        # Wait for common form containers to load
        await self.page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)  # Give more time for dynamic content
        
        # Try to find and click common cookie consent buttons
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
        
        # Scroll through the page to trigger lazy-loaded content
        await self.page.evaluate('''async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 200;
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }''')
        
        await asyncio.sleep(1)  # Wait after scrolling
        
        # Find all potential form elements - expanded selectors
        selectors = [
            'input:not([type="hidden"])',  # All inputs except hidden
            'select',
            'textarea',
            '[role="textbox"]',
            '[contenteditable="true"]',
            'div[role="combobox"]',
            'div[role="listbox"]',
            'div[role="option"]',
            'div[role="radio"]',
            'div[role="checkbox"]',
            'button:not([type="submit"])',
            'label',
            'div[class*="upload"], div[class*="file"], div[class*="drop"]',
            'div[data-test*="upload"], div[data-test*="file"]',
            'div[class*="form"], form',
            'div[class*="field"], div[class*="input"]',
            'div[data-test*="field"], div[data-test*="input"]',
            'div[class*="container"][aria-label*="upload" i]',
            'div[class*="drag"], div[class*="drop"]',
            'div[class*="browse"]',
            'div[class*="select"]',
            'div[class*="button"]',
            'button[class*="upload"], button[class*="file"]',
            'button[class*="browse"], button[class*="select"]',
            'button[class*="add"], button[class*="new"]',
            'button[class*="attach"], button[class*="document"]',
            'button[class*="cv"], button[class*="resume"]',
            'button[class*="browse"], button[class*="choose"]',
            'button[class*="click"], button[class*="upload"]',
            'button[class*="file"], button[class*="document"]',
            'button[class*="attach"], button[class*="add"]',
            'button[class*="select"], button[class*="choose"]',
            'button[class*="browse"], button[class*="upload"]'
        ]
        
        all_elements = []
        for selector in selectors:
            elements = await self.page.query_selector_all(selector)
            all_elements.extend(elements)
        
        print(f"Found {len(all_elements)} potential form elements")
        
        # Process each element with detailed logging
        for i, element in enumerate(all_elements, 1):
            try:
                # Get basic info first for better debugging
                tag = await element.get_property('tagName')
                element_id = await element.get_attribute('id') or ''
                element_type = (await element.get_attribute('type') or '').lower()
                element_class = await element.get_attribute('class') or ''
                
                # Check if element is potentially a file input or container
                is_potential_upload = (
                    element_type == 'file' or
                    'upload' in element_type or
                    'file' in element_type or
                    'upload' in element_class.lower() or
                    'file' in element_class.lower() or
                    'drop' in element_class.lower() or
                    'attach' in element_class.lower()
                )
                
                # Force make file inputs visible for detection
                if is_potential_upload:
                    await self.page.evaluate('''element => {
                        element.style.display = 'block';
                        element.style.visibility = 'visible';
                        element.style.opacity = '1';
                        element.style.position = 'static';
                        element.style.width = 'auto';
                        element.style.height = 'auto';
                        element.removeAttribute('hidden');
                        element.removeAttribute('aria-hidden');
                    }''', element)
                
                # Check visibility with more tolerance for file inputs
                is_visible = await element.is_visible()
                if not is_visible and not is_potential_upload:
                    print(f"  ⏩ Skipping hidden element: {tag} id={element_id} type={element_type}")
                    continue
                    
                print(f"🔍 Processing element {i}/{len(all_elements)}: {tag} id={element_id} type={element_type} class={element_class}")
                
                # Get element properties
                tag = await element.get_attribute('tagName')
                element_type = await element.get_attribute('type') or ''
                element_id = await element.get_attribute('id') or ''
                name = await element.get_attribute('name') or ''
                
                # Get outer HTML for LLM analysis
                outer_html = await self.get_element_html(element)
                
                # Only use LLM if explicitly enabled
                llm_info = {}
                if self.llm_detector:
                    try:
                        llm_info = await self.llm_detector.detect_field_type(
                            outer_html, 
                            name or element_id or f"field_{len(self.fields)}"
                        )
                    except Exception as e:
                        print(f"⚠️  LLM analysis skipped: {e}")
                        llm_info = {}
                
                # Get XPath
                xpath = await self.page.evaluate('''(element) => {
                    if (element.id) return `//*[@id="${element.id}"]`;
                    
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
                }''', element)
                
                # Get label
                label = ''
                try:
                    label = await self.page.evaluate('''(element) => {
                        // Try to find associated label
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
                        
                        // Try to find previous text node
                        let prev = element.previousSibling;
                        while (prev) {
                            if (prev.nodeType === 3 && prev.textContent.trim()) {  // Text node
                                return prev.textContent.trim();
                            }
                            prev = prev.previousSibling;
                        }
                        
                        return '';
                    }''', element)
                except:
                    pass
                
                # Create field info - only include essential fields by default
                field_info = {
                    'xpath': xpath,
                    'tag': (tag or '').lower(),
                    'type': (element_type or 'text').lower(),
                    'name': name or '',
                    'id': element_id or '',
                    'label': label or '',
                    'required': await element.evaluate('''el => 
                        el.required || 
                        el.getAttribute("aria-required") === "true" || 
                        el.hasAttribute("required") ||
                        el.closest('[required]') !== null
                    '''),
                    'disabled': await element.evaluate('el => el.disabled'),
                    'isFileInput': (element_type or '').lower() == 'file',
                    'accept': await element.get_attribute('accept') or ''
                }
                
                # Only include LLM info if explicitly enabled
                if self.llm_detector and llm_info:
                    field_info['llm_info'] = llm_info
                
                # Clean up label
                if field_info['label']:
                    field_info['label'] = ' '.join(field_info['label'].split())
                
                self.fields.append(field_info)
                
            except Exception as e:
                print(f"⚠️  Error processing element: {e}")
                continue
        
        print(f"✅ Found {len(self.fields)} form fields")

    async def save_mapping(self):
        """Save the detected form fields to a JSON file with enhanced LLM data."""
        # Clean up the fields to be JSON serializable
        serializable_fields = []
        for field in self.fields:
            # Create a clean field dictionary with only the most important data
            clean_field = {
                'xpath': field.get('xpath', ''),
                'tag': field.get('tag', ''),
                'type': field.get('type', 'text'),
                'name': field.get('name', ''),
                'id': field.get('id', ''),
                'label': field.get('label', ''),
                'required': field.get('required', False),
                'disabled': field.get('disabled', False),
                'readOnly': field.get('readOnly', False),
                'multiple': field.get('multiple', False),
                'accept': field.get('accept', ''),
                'isFileInput': field.get('isFileInput', False),
            }
            
            # Add LLM info if available
            llm_info = field.get('llm_info')
            if llm_info and isinstance(llm_info, dict):
                clean_field.update({
                    'llm_type': llm_info.get('type'),
                    'llm_description': llm_info.get('description', ''),
                    'llm_required': llm_info.get('required', False)
                })
            
            # Ensure all values are JSON serializable
            for key, value in clean_field.items():
                if isinstance(value, (bool, int, float, str)) or value is None:
                    continue
                try:
                    json.dumps(value)
                except (TypeError, OverflowError):
                    clean_field[key] = str(value)
            
            serializable_fields.append(clean_field)
        
        # Save to file with pretty printing
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_fields, f, indent=2, ensure_ascii=False)
        
        # Also save a more detailed version for debugging
        debug_file = os.path.splitext(self.output_file)[0] + '_debug.json'
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(self.fields, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ Mapping saved to {self.output_file}")
        print(f"🔍 Debug data saved to {debug_file}")
        return True

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
    import argparse
    import os
    import sys
    
    parser = argparse.ArgumentParser(description='Automatically map form fields on a webpage.')
    parser.add_argument('url', help='URL of the webpage with the form')
    parser.add_argument('-o', '--output', default='form_map_auto.json', 
                      help='Output JSON file (default: form_map_auto.json)')
    parser.add_argument('--ollama-url', default=None,
                      help='Ollama server URL (e.g., http://localhost:11434). If not provided, LLM analysis is disabled.')
    parser.add_argument('--use-llm', action='store_true',
                      help='Enable LLM analysis (requires --ollama-url)')
    
    args = parser.parse_args()
    
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    try:
        print(f"🔍 Starting form field detection on {args.url}")
        
        # Initialize the mapper with Ollama URL
        mapper = AutoFormMapper(
            url=args.url,
            output_file=args.output,
            ollama_url=args.ollama_url,
            use_llm=args.use_llm
        )
        
        if args.use_llm and not args.ollama_url:
            print("⚠️  Warning: --use-llm requires --ollama-url. LLM analysis will be disabled.")
        
        # Run the mapping process
        asyncio.run(mapper.run())
        
        print("✅ Form mapping completed successfully!")
        print(f"📋 Mapped {len(mapper.fields)} form fields to {args.output}")
        
        if mapper.llm_detector:
            print(f"🤖 Using local LLM (Mistral 7B) for field analysis at {args.ollama_url}")
        else:
            print("ℹ️  Local LLM analysis is disabled")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
