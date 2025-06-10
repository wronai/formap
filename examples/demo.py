#!/usr/bin/env python3
"""
Formap Demo: Automating Form Filling

This script demonstrates how to use Formap to automatically fill out a form.
It includes both a simple example and an advanced example with file uploads.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import formap
sys.path.insert(0, str(Path(__file__).parent.parent))

from formap import FormDetector, FormFiller, FormData
from formap.models.field import FieldType
from playwright.async_api import async_playwright

# Get the absolute path to the example form
EXAMPLE_FORM = str(Path(__file__).parent / "simple_form.html")


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

async def run_simple_example():
    """Run a simple example of form detection and filling."""
    print("🚀 Starting Formap Demo - Simple Example")
    print("=" * 80)
    
    # Initialize Playwright
    playwright, browser, context, page = await init_browser(headless=False)
    
    try:
        # Create a form data object with the values we want to fill
        form_data = FormData(
            fields={
                "username": "testuser",
                "email": "test@example.com",
                "password": "s3cur3p@ssw0rd",
                "fullname": "Test User",
                "bio": "This is a test bio for demonstration purposes.",
                "country": "us",
                "subscribe": True,
            }
        )
        
        # Create a FormDetector instance with the page object
        print(f"🔍 Detecting form fields in {EXAMPLE_FORM}...")
        
        # Navigate to the form
        await page.goto(f"file://{EXAMPLE_FORM}")
        
        # Initialize the detector
        detector = FormDetector(page=page)
        
        # Detect form fields
        fields = await detector.detect(url=f"file://{EXAMPLE_FORM}")
        
        print(f"✅ Found {len(fields)} form fields:")
        for field in fields:
            print(f"   - {field.name} ({field.field_type.value})")
        
        # Create a FormFiller instance with the page
        print("\n🖊️  Filling out the form...")
        
        # Initialize the filler
        filler = FormFiller(page=page)
        
        # Fill the form with our data
        success = await filler.fill(
            url=f"file://{EXAMPLE_FORM}",
            form_data=form_data,
            field_mapping=fields
        )
        
        if success:
            print("✅ Form filled successfully!")
        else:
            print("❌ Failed to fill the form")
            
        # Wait for a moment to see the result
        await asyncio.sleep(3)
                
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    finally:
        # Close the browser
        await close_browser(playwright, browser, context)
    
    print("\n🎉 Demo completed!")


async def run_advanced_example():
    """Run an advanced example with file uploads and more complex form handling."""
    print("\n🚀 Starting Formap Demo - Advanced Example")
    print("=" * 80)
    
    # Initialize Playwright
    playwright, browser, context, page = await init_browser(headless=False)
    
    try:
        # Create a temporary file for upload
        upload_dir = Path("examples/uploads")
        upload_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a sample file to upload
        sample_file = upload_dir / "resume.txt"
        with open(sample_file, "w") as f:
            f.write("This is a sample resume.\n")
            f.write("Name: Test User\n")
            f.write("Skills: Python, Testing, Automation\n")
        
        # Create form data with file upload
        form_data = FormData(
            fields={
                "username": "advanceduser",
                "email": "advanced@example.com",
                "password": "@dv@ncedP@ss123",
                "fullname": "Advanced User",
                "bio": "This is an advanced test with file uploads.",
                "country": "uk",
                "subscribe": False,
            },
            files={
                # This would be the name of the file input field in the form
                # For this example, we're just showing how it would work
                # In a real form, you would have an <input type="file"> with name="resume"
                "resume": str(sample_file.absolute())
            }
        )
        
        # Navigate to the form
        await page.goto(f"file://{EXAMPLE_FORM}")
        
        # Create a FormDetector instance with custom options
        print(f"🔍 Detecting form fields in {EXAMPLE_FORM} with advanced options...")
        
        # Initialize the detector with custom options
        detector = FormDetector(page=page)
        
        # Detect form fields with URL
        fields = await detector.detect(url=f"file://{EXAMPLE_FORM}")
        
        print(f"✅ Found {len(fields)} form fields:")
        for field in fields:
            print(f"   - {field.name} ({field.field_type.value})")
        
        # Create a FormFiller instance with the page
        print("\n🖊️  Filling out the form with advanced options...")
        
        # Initialize the filler
        filler = FormFiller(page=page)
        
        # Fill the form with our data
        success = await filler.fill(
            url=f"file://{EXAMPLE_FORM}",
            form_data=form_data,
            field_mapping=fields,
            upload_dir=str(upload_dir.absolute())  # Directory to look for files to upload
        )
        
        if success:
            print("✅ Form filled successfully!")
        else:
            print("❌ Failed to fill the form")
        
        # Wait for a moment to see the result
        await asyncio.sleep(3)
        
        # Clean up
        if sample_file.exists():
            sample_file.unlink()
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    finally:
        # Close the browser
        await close_browser(playwright, browser, context)
    
    print("\n🎉 Advanced demo completed!")


async def main():
    """Run all examples."""
    print("Formap Demo - Automated Form Filling")
    print("-" * 80)
    
    try:
        # Run the simple example
        await run_simple_example()
        
        # Run the advanced example
        await run_advanced_example()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🎉 Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())
