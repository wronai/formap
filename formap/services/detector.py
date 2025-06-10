"""Form field detection service."""
import asyncio
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from urllib.parse import urljoin

from playwright.async_api import Page, ElementHandle, Locator

from formap.models.field import FormField, FieldType, FieldOption


@dataclass
class DetectionOptions:
    """Options for form field detection."""
    detect_hidden: bool = False
    include_buttons: bool = False
    include_hidden: bool = False
    max_fields: Optional[int] = None
    field_selector: str = """
        input:not([type="hidden"]),
        select,
        textarea,
        [role="textbox"],
        [contenteditable="true"]
    """


class FormDetector:
    """Service for detecting form fields on a web page."""

    def __init__(self, page: Page):
        self.page = page
        self._seen_elements: Set[str] = set()

    async def detect(
        self,
        url: str,
        options: Optional[DetectionOptions] = None
    ) -> List[FormField]:
        """
        Detect form fields on the current page.
        
        Args:
            url: The URL of the page being scanned
            options: Detection options
            
        Returns:
            List of detected form fields
        """
        if options is None:
            options = DetectionOptions()
            
        self._seen_elements.clear()
        
        # Navigate to the URL if not already there
        if self.page.url != url:
            await self.page.goto(url, wait_until="networkidle")
        
        # Handle cookie consent if present
        await self._handle_cookie_consent()
        
        # Scroll to trigger lazy-loaded content
        await self._scroll_page()
        
        # Find all potential form elements
        elements = await self._find_form_elements(options)
        
        # Process elements into form fields
        fields = []
        for element in elements:
            if options.max_fields and len(fields) >= options.max_fields:
                break
                
            try:
                field = await self._process_element(element, options)
                if field and field.xpath not in self._seen_elements:
                    fields.append(field)
                    self._seen_elements.add(field.xpath)
            except Exception as e:
                print(f"Error processing element: {e}")
                continue
                
        return fields

    async def _find_form_elements(self, options: DetectionOptions) -> List[ElementHandle]:
        """Find all potential form elements on the page."""
        # First try with the custom selector
        elements = await self.page.query_selector_all(options.field_selector)
        
        # If no elements found, try a more aggressive approach
        if not elements:
            elements = await self.page.query_selector_all("input, select, textarea, [role=textbox], [contenteditable=true]")
        
        # Filter out hidden elements if needed
        if not options.detect_hidden:
            visible_elements = []
            for element in elements:
                try:
                    if await element.is_visible():
                        visible_elements.append(element)
                except:
                    continue
            elements = visible_elements
            
        return elements

    async def _process_element(
        self, 
        element: ElementHandle,
        options: DetectionOptions
    ) -> Optional[FormField]:
        """Process a single form element."""
        # Get basic element info
        tag_name = (await element.get_property('tagName') or '').lower()
        element_type = (await element.get_attribute('type') or '').lower()
        element_id = await element.get_attribute('id') or ''
        name = await element.get_attribute('name') or ''
        
        # Skip elements we can't process
        if not tag_name or (not name and not element_id):
            return None
            
        # Skip hidden elements if not requested
        is_visible = await element.is_visible()
        if not is_visible and not options.detect_hidden:
            return None
            
        # Skip buttons if not requested
        if element_type == 'submit' and not options.include_buttons:
            return None
            
        # Skip hidden fields if not requested
        if element_type == 'hidden' and not options.include_hidden:
            return None
            
        # Get XPath
        xpath = await self._get_xpath(element)
        
        # Get field type
        field_type = self._determine_field_type(tag_name, element_type)
        
        # Get label
        label = await self._get_label_for_element(element, element_id, name)
        
        # Get other attributes
        placeholder = await element.get_attribute('placeholder') or ''
        required = await element.evaluate('el => el.required || el.getAttribute("aria-required") === "true"')
        disabled = await element.evaluate('el => el.disabled')
        read_only = await element.evaluate('el => el.readOnly')
        value = await element.get_attribute('value') or ''
        
        # Handle special cases
        options_list = []
        multiple = False
        accept = ''
        
        if field_type == FieldType.SELECT:
            options_list = await self._get_select_options(element)
            multiple = await element.evaluate('el => el.multiple')
        elif field_type == FieldType.FILE:
            accept = await element.get_attribute('accept') or ''
        elif field_type == FieldType.CHECKBOX:
            checked = await element.is_checked()
            value = 'true' if checked else 'false'
        
        return FormField(
            name=name or element_id or f"field_{len(self._seen_elements)}",
            field_type=field_type,
            xpath=xpath,
            label=label,
            placeholder=placeholder,
            value=value,
            required=required,
            disabled=disabled,
            read_only=read_only,
            multiple=multiple,
            accept=accept,
            options=options_list
        )

    async def _get_xpath(self, element: ElementHandle) -> str:
        """Get XPath for the element."""
        return await self.page.evaluate('''(element) => {
            if (!element || !element.ownerDocument) return '';
            
            // If element has an ID, use that for the XPath
            if (element.id) {
                const id = element.id.replace(/'/g, "\\'");
                return `//*[@id="${id}"]`;
            }
            
            // Otherwise, build the XPath by walking up the DOM
            const parts = [];
            let current = element;
            
            while (current && current.nodeType === Node.ELEMENT_NODE) {
                let index = 1;
                let sibling = current.previousElementSibling;
                
                while (sibling) {
                    if (sibling.nodeName === current.nodeName) index++;
                    sibling = sibling.previousElementSibling;
                }
                
                const tag = current.tagName.toLowerCase();
                const part = index > 1 ? `${tag}[${index}]` : tag;
                parts.unshift(part);
                
                // If we find an ID on a parent, use that for better XPath
                if (current.id) {
                    const id = current.id.replace(/'/g, "\\'");
                    parts.unshift(`//*[@id="${id}"]`);
                    break;
                }
                
                current = current.parentElement;
            }
            
            return parts.length ? `//${parts.join('/')}` : '';
        }''', element)

    def _determine_field_type(self, tag_name: str, element_type: str) -> FieldType:
        """Determine the field type based on tag name and type attribute."""
        if tag_name == 'input':
            type_map = {
                'text': FieldType.TEXT,
                'email': FieldType.EMAIL,
                'password': FieldType.PASSWORD,
                'tel': FieldType.TEL,
                'number': FieldType.NUMBER,
                'date': FieldType.DATE,
                'checkbox': FieldType.CHECKBOX,
                'radio': FieldType.RADIO,
                'file': FieldType.FILE,
                'submit': FieldType.SUBMIT,
                'button': FieldType.BUTTON,
                'hidden': FieldType.HIDDEN,
            }
            return type_map.get(element_type, FieldType.TEXT)
        elif tag_name == 'select':
            return FieldType.SELECT
        elif tag_name == 'textarea':
            return FieldType.TEXTAREA
        return FieldType.UNKNOWN

    async def _get_label_for_element(
        self, 
        element: ElementHandle, 
        element_id: str, 
        name: str
    ) -> str:
        """Get label text for the form element."""
        # Try to find by 'for' attribute
        if element_id:
            try:
                label = await self.page.query_selector(f'label[for="{element_id}"]')
                if label:
                    text = await label.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                pass
        
        # Try to find parent label
        try:
            parent = await element.query_selector('xpath=..')
            if parent:
                parent_tag = await parent.get_property('tagName')
                if parent_tag and parent_tag.lower() == 'label':
                    text = await parent.text_content()
                    if text and text.strip():
                        return text.strip()
        except:
            pass
        
        # Try to find by name
        if name:
            try:
                label = await self.page.query_selector(f'label[for="{name}"]')
                if label:
                    text = await label.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                pass
        
        # Try to find by text near the input
        try:
            text = await element.evaluate('''(el) => {
                // Get all text nodes near the input
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    { 
                        acceptNode: (node) => {
                            // Skip empty or whitespace-only text nodes
                            if (!node.textContent || !node.textContent.trim()) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            // Get the parent element of the text node
                            const parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;
                            
                            // Skip script and style elements
                            if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            
                            // Check if the element is near our target
                            const elRect = el.getBoundingClientRect();
                            const rect = parent.getBoundingClientRect();
                            
                            // Check if the element is above and close to our input
                            const isAbove = rect.bottom <= elRect.top + 10;
                            const isNear = Math.abs(rect.right - elRect.left) < 100 || 
                                         Math.abs(rect.left - elRect.right) < 100;
                            
                            return (isAbove && isNear) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                        }
                    }
                );
                
                let node;
                let text = '';
                while (node = walker.nextNode()) {
                    text += ' ' + node.textContent.trim();
                    if (text.length > 100) break; // Limit text length
                }
                return text.trim();
            }''')
            
            if text and len(text) < 100:  # Arbitrary limit to avoid too much text
                return text
        except Exception as e:
            print(f"Error finding label by proximity: {e}")
        
        return ''

    async def _get_select_options(self, select_element: ElementHandle) -> List[FieldOption]:
        """Get options for a select element."""
        options = await select_element.query_selector_all('option')
        result = []
        
        for option in options:
            try:
                value = await option.get_attribute('value') or ''
                text = await option.text_content() or ''
                selected = await option.evaluate('el => el.selected')
                result.append(FieldOption(value=value, text=text.strip(), selected=selected))
            except:
                continue
        
        return result

    async def _handle_cookie_consent(self):
        """Handle cookie consent popups if present."""
        cookie_selectors = [
            'button#onetrust-accept-btn-handler',
            'button[aria-label*="cookie" i], button[class*="cookie" i]',
            'button:has-text("Accept")',
            'button:has-text("Akzeptieren")',
            'button:has-text("Zustimmen")',
            'button:has-text("Agree")',
            'button:has-text("Accept All")',
            'button:has-text("Accept all")',
            '.cookie-banner .accept',
            '.cookie-consent .accept',
            '#cookie-consent-accept',
            '.cookie-accept',
            '.accept-cookies'
        ]
        
        for selector in cookie_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible() and await element.is_enabled():
                    await element.click()
                    await asyncio.sleep(1)  # Wait for any animations
                    break
            except:
                continue

    async def _scroll_page(self):
        """Scroll the page to trigger lazy-loaded content."""
        try:
            # Scroll to bottom
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
            
            # Scroll back to top
            await self.page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(0.5)
        except:
            pass
