#!/usr/bin/env python3
"""
Job Application Form Filler

This script demonstrates how to use Formap to fill out a job application form.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import formap
sys.path.insert(0, str(Path(__file__).parent.parent))

from formap import FormDetector, FormFiller, FormData
from playwright.async_api import async_playwright

# Job application URL
JOB_URL = "https://bewerbung.jobs/325696/buchhalter-m-w-d"

async def init_browser(headless: bool = False):
    """Initialize Playwright browser and page."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()
    return playwright, browser, context, page

async def close_browser(playwright, browser, context):
    """Close Playwright resources."""
    await context.close()
    await browser.close()
    await playwright.stop()

async def fill_job_application():
    """Fill out a job application form."""
    print(f"🚀 Starting Job Application: {JOB_URL}")
    print("=" * 80)
    
    # Initialize Playwright
    playwright, browser, context, page = await init_browser(headless=False)
    
    try:
        # Sample job application data
        application_data = FormData(
            fields={
                # Personal Information
                "anrede": "Herr",  # or "Frau"
                "vorname": "Max",
                "nachname": "Mustermann",
                "email": "max.mustermann@example.com",
                "telefon": "+49123456789",
                "strasse": "Musterstraße 123",
                "plz": "12345",
                "ort": "Musterstadt",
                "geburtsdatum": "01.01.1980",
                "verfuegbar_ab": "01.08.2023",
                "gehalt": "50000",
                
                # Education
                "ausbildung_abschluss": "Bachelor of Science",
                "ausbildung_fachrichtung": "Buchhaltung",
                "ausbildung_jahr": "2010",
                
                # Work Experience
                "berufserfahrung": "5 Jahre Erfahrung in der Buchhaltung",
                "letzter_arbeitgeber": "Musterfirma GmbH",
                "letzte_position": "Buchhalter",
                
                # Additional Information
                "fuehrerschein": "B",
                "sprachkenntnisse": "Deutsch (Muttersprache), Englisch (Fließend)",
                "sonstiges": "Ich bin sehr motiviert und lerne schnell.",
            },
            files={
                # These would be the actual file paths on your system
                "lebenslauf": "path/to/lebenslauf.pdf",
                "zeugnisse": "path/to/zeugnisse.pdf",
                "anhang": "path/to/anhang.pdf"
            }
        )
        
        # Navigate to the job application page
        print(f"🌐 Opening {JOB_URL}...")
        await page.goto(JOB_URL, wait_until="networkidle")
        
        # Wait for the cookie consent dialog and accept if it appears
        try:
            await page.wait_for_selector("button:has-text('Alle akzeptieren')", timeout=5000)
            await page.click("button:has-text('Alle akzeptieren')")
            print("✅ Accepted cookies")
        except Exception as e:
            print("ℹ️ No cookie consent dialog found or could not accept")
        
        # Wait for the form to be visible
        print("⏳ Waiting for the form to load...")
        try:
            await page.wait_for_selector('form', timeout=10000)
            print("✅ Form found on the page")
        except Exception as e:
            print("❌ Form not found on the page")
            print("Trying to find form elements directly...")
        
        # Take a screenshot for debugging
        await page.screenshot(path='form_page.png')
        print("📸 Screenshot saved as form_page.png")
        
        # Try to find form elements using more specific selectors
        print("🔍 Looking for form elements...")
        
        # Look for common form field types
        input_fields = await page.query_selector_all('input, textarea, select')
        print(f"Found {len(input_fields)} potential form fields")
        
        # Print information about the found fields
        for i, field in enumerate(input_fields[:10]):
            try:
                field_type = await field.get_attribute('type') or 'text'
                field_name = await field.get_attribute('name') or f'field_{i}'
                field_id = await field.get_attribute('id') or ''
                print(f"   - {field_name} ({field_type}) [id: {field_id}]")
            except Exception as e:
                print(f"   - Could not get field info: {str(e)}")
        
        if len(input_fields) > 10:
            print(f"   ... and {len(input_fields) - 10} more fields")
        
        # Try to fill the form using direct element interaction
        print("\n🖊️  Attempting to fill form directly...")
        
        # Map of field names to values
        field_map = {
            # Personal Information
            'anrede': 'Herr',
            'vorname': 'Max',
            'nachname': 'Mustermann',
            'email': 'max.mustermann@example.com',
            'telefon': '+49123456789',
            'strasse': 'Musterstraße 123',
            'plz': '12345',
            'ort': 'Musterstadt',
            'geburtsdatum': '01.01.1980',
            'verfuegbar_ab': '01.08.2023',
            'gehalt': '50000',
        }
        
        filled_count = 0
        for field_name, value in field_map.items():
            try:
                # Try different selectors for each field
                selectors = [
                    f'input[name="{field_name}"]',
                    f'input[id*="{field_name}"]',
                    f'input[placeholder*="{field_name}" i]',
                    f'//*[contains(translate(@name, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{field_name}")]',
                    f'//*[contains(translate(@id, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{field_name}")]',
                    f'//*[contains(translate(@placeholder, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{field_name}")]'
                ]
                
                filled = False
                for selector in selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=1000)
                        if element:
                            await element.fill(value)
                            print(f"   ✓ Filled {field_name}: {value}")
                            filled = True
                            filled_count += 1
                            break
                    except:
                        continue
                        
                if not filled:
                    print(f"   ✗ Could not find field: {field_name}")
                    
            except Exception as e:
                print(f"   ! Error filling {field_name}: {str(e)}")
        
        print(f"\n✅ Successfully filled {filled_count} out of {len(field_map)} fields")
        
        # Initialize the form filler
        print("\n🖊️  Filling out the job application form...")
        filler = FormFiller(page=page)
        
        # Fill the form with our data
        success = await filler.fill(
            url=JOB_URL,
            form_data=application_data,
            field_mapping=fields,
            upload_dir=str(Path.home() / "Documents")  # Look for files in Documents folder
        )
        
        if success:
            print("✅ Job application form filled successfully!")
            
            # Optional: Uncomment to submit the form
            # print("\n📤 Submitting the application...")
            # await page.click("button[type='submit']")
            # await asyncio.sleep(3)  # Wait for submission
            # print("✅ Application submitted!")
            
        else:
            print("❌ Failed to fill the job application form")
        
        # Wait for a moment to see the result
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the browser
        await close_browser(playwright, browser, context)
    
    print("\n🎉 Job application process completed!")

async def main():
    """Run the job application example."""
    print("Job Application Form Filler")
    print("-" * 80)
    
    try:
        await fill_job_application()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🎉 Process completed!")

if __name__ == "__main__":
    asyncio.run(main())
