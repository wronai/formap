"""Form filling service."""
import asyncio
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from playwright.async_api import Page, ElementHandle, FilePayload

from formap.models.field import FormField, FormData, FieldType

logger = logging.getLogger(__name__)

class FormFiller:
    """Service for filling web forms based on field mappings."""

    def __init__(self, page: Page):
        self.page = page
        self.upload_dir = Path.home() / "uploads"
        
    async def fill(
        self,
        url: str,
        form_data: Union[Dict, FormData],
        field_mapping: List[FormField],
        headless: bool = True,
        wait_timeout: int = 30000,
        upload_dir: Optional[str] = None
    ) -> bool:
        """
        Fill a form using the provided data and field mapping.
        
        Args:
            url: The URL of the form
            form_data: Form data to fill (can be dict or FormData)
            field_mapping: List of FormField objects
            headless: Whether to run in headless mode
            wait_timeout: Timeout for page operations in ms
            upload_dir: Optional directory for file uploads
            
        Returns:
            bool: True if form was filled successfully, False otherwise
        """
        if not isinstance(form_data, FormData):
            form_data = FormData(fields=form_data)
            
        if upload_dir:
            self.upload_dir = Path(upload_dir)
            
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Filling form at {url}")
        
        try:
            # Navigate to the URL
            await self.page.goto(url, wait_until="networkidle", timeout=wait_timeout)
            
            # Handle cookie consent if present
            await self._handle_cookie_consent()
            
            # Convert field mapping to dict for easier access
            fields_by_name = {field.name: field for field in field_mapping}
            
            # Fill non-file fields first
            await self._fill_non_file_fields(form_data, fields_by_name)
            
            # Handle file uploads
            if form_data.files:
                await self._handle_file_uploads(form_data, fields_by_name)
                
            logger.info("Form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling form: {e}", exc_info=True)
            return False
    
    async def _fill_non_file_fields(
        self, 
        form_data: FormData,
        fields_by_name: Dict[str, FormField]
    ) -> None:
        """Fill all non-file form fields."""
        for field_name, field in fields_by_name.items():
            if field.field_type == FieldType.FILE:
                continue
                
            value = form_data.get_field_value(field_name)
            if value is None:
                continue
                
            try:
                element = await self.page.wait_for_selector(
                    f'xpath={field.xpath}',
                    state='attached',
                    timeout=5000
                )
                
                if not element:
                    logger.warning(f"Could not find element for field: {field_name}")
                    continue
                    
                # Scroll element into view
                await element.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(200)  # Small delay for scrolling
                
                # Handle different field types
                if field.field_type == FieldType.CHECKBOX:
                    is_checked = str(value).lower() in ('true', '1', 'yes', 'on')
                    current_checked = await element.is_checked()
                    if is_checked != current_checked:
                        await element.click()
                    
                elif field.field_type == FieldType.RADIO:
                    if str(value) == str(field.value):
                        await element.check()
                        
                elif field.field_type == FieldType.SELECT:
                    await element.select_option(str(value))
                    
                else:  # text, email, password, etc.
                    await element.click()
                    await element.fill('')  # Clear existing value
                    await element.type(str(value), delay=50)  # Type with delay
                    
                logger.info(f"Filled field: {field_name} = {value}")
                
                # Small delay between fields
                await self.page.wait_for_timeout(100)
                
            except Exception as e:
                logger.warning(f"Error filling field {field_name}: {e}")
    
    async def _handle_file_uploads(
        self, 
        form_data: FormData, 
        fields_by_name: Dict[str, FormField]
    ) -> None:
        """Handle file upload fields."""
        for field_name, file_path in form_data.files.items():
            if field_name not in fields_by_name:
                logger.warning(f"No mapping found for file field: {field_name}")
                continue
                
            field = fields_by_name[field_name]
            
            # Resolve the file path
            file_path = Path(file_path)
            if not file_path.is_absolute():
                file_path = self.upload_dir / file_path
                
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
                
            try:
                element = await self.page.wait_for_selector(
                    f'xpath={field.xpath}',
                    state='attached',
                    timeout=5000
                )
                
                if not element:
                    logger.warning(f"Could not find file input for field: {field_name}")
                    continue
                    
                # Scroll element into view
                await element.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(200)
                
                # Set the file input
                await element.set_input_files(str(file_path))
                logger.info(f"Uploaded file for {field_name}: {file_path.name}")
                
                # Wait for upload to complete if needed
                await self.page.wait_for_timeout(1000)
                
            except Exception as e:
                logger.error(f"Error uploading file for {field_name}: {e}")
    
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

    def find_matching_file(self, field_name: str, file_types: Optional[List[str]] = None) -> Optional[Path]:
        """
        Find a file in the upload directory that matches the field name.
        
        Args:
            field_name: Name of the form field
            file_types: List of file extensions to look for (e.g., ['.pdf', '.docx'])
            
        Returns:
            Path to the matching file, or None if not found
        """
        if not self.upload_dir.exists():
            return None
            
        if file_types is None:
            file_types = ['.pdf', '.doc', '.docx', '.txt', '.odt']
            
        # Clean up field name for matching
        clean_name = ''.join(c if c.isalnum() else '_' for c in field_name.lower())
        
        # Common field name variations
        field_variations = {
            'cv': ['cv', 'resume', 'curriculum', 'lebenslauf'],
            'resume': ['cv', 'resume', 'curriculum', 'lebenslauf'],
            'cover_letter': ['cover', 'letter', 'anschreiben', 'motivation'],
            'photo': ['photo', 'picture', 'bild', 'portrait']
        }
        
        # Add variations based on field name
        for key, variations in field_variations.items():
            if key in clean_name:
                variations.extend([key])
                break
        else:
            variations = [clean_name]
        
        # Look for matching files
        for file_path in self.upload_dir.glob('*'):
            if not file_path.is_file():
                continue
                
            # Check file extension
            if file_path.suffix.lower() not in file_types:
                continue
                
            # Check if filename contains any of the variations
            filename = file_path.stem.lower()
            if any(variation in filename for variation in variations):
                return file_path
                
        # If no exact match, return the first file with a matching extension
        for file_path in self.upload_dir.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_types:
                return file_path
                
        return None
