from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from playwright.async_api import ElementHandle, Page
from .logger import log

class FieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    TEL = "tel"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    FILE = "file"
    HIDDEN = "hidden"
    SUBMIT = "submit"
    BUTTON = "button"
    UNKNOWN = "unknown"

@dataclass
class FormField:
    xpath: str
    name: str
    field_type: FieldType
    label: str = ""
    placeholder: str = ""
    required: bool = False
    value: str = ""
    options: List[Dict[str, str]] = None
    multiple: bool = False
    accept: str = ""
    is_visible: bool = True
    is_interactable: bool = True
    
    def to_dict(self) -> dict:
        result = asdict(self)
        result["field_type"] = self.field_type.value
        return result

class FormDetector:
    def __init__(self, page: Page):
        self.page = page
        self._seen_elements: Set[str] = set()
    
    async def detect_form_fields(self) -> List[FormField]:
        """Detect all form fields on the page."""
        log.info("Starting form field detection")
        
        # Get all potential form elements
        input_selectors = [
            'input:not([type="hidden"])',
            'select',
            'textarea',
            '[role="textbox"]',
            '[contenteditable="true"]'
        ]
        
        all_elements = []
        for selector in input_selectors:
            elements = await self.page.query_selector_all(selector)
            all_elements.extend(elements)
        
        log.info(f"Found {len(all_elements)} potential form elements")
        
        fields = []
        for element in all_elements:
            try:
                field = await self._process_element(element)
                if field and field.xpath not in self._seen_elements:
                    fields.append(field)
                    self._seen_elements.add(field.xpath)
            except Exception as e:
                log.error(f"Error processing element: {e}", exc_info=True)
        
        log.info(f"Detected {len(fields)} form fields")
        return fields
    
    async def _process_element(self, element: ElementHandle) -> Optional[FormField]:
        """Process a single form element and return its metadata."""
        # Get basic element info
        tag_name = (await element.get_property('tagName')).lower()
        element_type = (await element.get_attribute('type') or '').lower()
        element_id = await element.get_attribute('id') or ''
        name = await element.get_attribute('name') or ''
        
        # Skip non-interactive elements
        is_visible = await element.is_visible()
        is_enabled = await element.is_enabled()
        if not is_visible or not is_enabled:
            log.debug(f"Skipping non-interactive element: {tag_name}[type={element_type}] id={element_id}")
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
        value = await element.get_attribute('value') or ''
        
        # Handle special cases
        options = []
        multiple = False
        accept = ''
        
        if field_type == FieldType.SELECT:
            options = await self._get_select_options(element)
            multiple = await element.evaluate('el => el.multiple')
        elif field_type == FieldType.FILE:
            accept = await element.get_attribute('accept') or ''
        
        return FormField(
            xpath=xpath,
            name=name or element_id or f"field_{len(self._seen_elements)}",
            field_type=field_type,
            label=label,
            placeholder=placeholder,
            required=required,
            value=value,
            options=options,
            multiple=multiple,
            accept=accept,
            is_visible=is_visible,
            is_interactable=is_enabled
        )
    
    async def _get_xpath(self, element: ElementHandle) -> str:
        """Get XPath for the element."""
        return await self.page.evaluate('''(element) => {
            if (element.id) return `//*[@id="${element.id}"]`;
            
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
                
                if (current.id) {
                    parts.unshift(`//*[@id="${current.id}"]`);
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
    
    async def _get_label_for_element(self, element: ElementHandle, element_id: str, name: str) -> str:
        """Get label text for the form element."""
        # Try to find by 'for' attribute
        if element_id:
            label = await self.page.query_selector(f'label[for="{element_id}"]')
            if label:
                return await label.inner_text() or ''
        
        # Try to find parent label
        parent = await element.query_selector('xpath=..')
        if parent:
            parent_tag = await parent.get_property('tagName')
            if parent_tag.lower() == 'label':
                return await parent.inner_text() or ''
        
        # Try to find by name
        if name:
            label = await self.page.query_selector(f'label[for="{name}"]')
            if label:
                return await label.inner_text() or ''
        
        # Try to find by text near the input
        try:
            # Get all text nodes near the input
            text = await element.evaluate('''(el) => {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    { acceptNode: (node) => {
                        const rect = node.parentElement.getBoundingClientRect();
                        const elRect = el.getBoundingClientRect();
                        return (rect.top <= elRect.top + 10 && rect.bottom >= elRect.top - 30) ?
                            NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
                    }}
                );
                
                let node;
                let text = '';
                while (node = walker.nextNode()) {
                    text += ' ' + node.textContent.trim();
                }
                return text.trim();
            }''')
            
            if text and len(text) < 100:  # Arbitrary limit to avoid too much text
                return text
        except Exception as e:
            log.debug(f"Error finding label by proximity: {e}")
        
        return ''
    
    async def _get_select_options(self, select_element: ElementHandle) -> List[Dict[str, str]]:
        """Get options for a select element."""
        options = await select_element.query_selector_all('option')
        result = []
        
        for option in options:
            value = await option.get_attribute('value') or ''
            text = await option.inner_text()
            result.append({"value": value, "text": text})
        
        return result
