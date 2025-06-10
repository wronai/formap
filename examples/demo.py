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
from typing import Dict, Any

# Add the parent directory to the path so we can import formap
sys.path.insert(0, str(Path(__file__).parent.parent))

from formap import FormDetector, FormFiller, FormData
from formap.models.field import FieldType

# Get the absolute path to the example form
EXAMPLE_FORM = str(Path(__file__).parent / "simple_form.html")


async def run_simple_example():
    """Run a simple example of form detection and filling."""
    print("🚀 Starting Formap Demo - Simple Example")
    print("=" * 80)
    
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
    
    # Create a FormDetector instance
    async with FormDetector() as detector:
        print(f"🔍 Detecting form fields in {EXAMPLE_FORM}...")
        
        # Detect form fields
        fields = await detector.detect(f"file://{EXAMPLE_FORM}")
        
        print(f"✅ Found {len(fields)} form fields:")
        for field in fields:
            print(f"   - {field.name} ({field.field_type.value})")
        
        # Create a FormFiller instance
        async with FormFiller() as filler:
            print("\n🖊️  Filling out the form...")
            
            # Fill the form with our data
            success = await filler.fill(
                url=f"file://{EXAMPLE_FORM}",
                form_data=form_data,
                field_mapping=fields,
                headless=False,  # Set to True to run in headless mode
                timeout=30000,    # 30 second timeout
            )
            
            if success:
                print("✅ Form filled successfully!")
            else:
                print("❌ Failed to fill the form")
    
    print("\n🎉 Demo completed!")


async def run_advanced_example():
    """Run an advanced example with file uploads and more complex form handling."""
    print("\n🚀 Starting Formap Demo - Advanced Example")
    print("=" * 80)
    
    # Create a temporary file for upload
    upload_dir = Path("examples/uploads")
    upload_dir.mkdir(exist_ok=True)
    
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
    
    # Create a FormDetector instance with custom options
    async with FormDetector() as detector:
        print(f"🔍 Detecting form fields in {EXAMPLE_FORM} with advanced options...")
        
        # Detect form fields with custom options
        fields = await detector.detect(
            url=f"file://{EXAMPLE_FORM}",
            detect_hidden=True,  # Include hidden fields
            include_buttons=True,  # Include buttons
            max_fields=20,        # Limit number of fields to detect
        )
        
        print(f"✅ Found {len(fields)} form fields:")
        for field in fields:
            print(f"   - {field.name} ({field.field_type.value})")
        
        # Create a FormFiller instance with custom options
        async with FormFiller() as filler:
            print("\n🖊️  Filling out the form with advanced options...")
            
            # Fill the form with our data
            success = await filler.fill(
                url=f"file://{EXAMPLE_FORM}",
                form_data=form_data,
                field_mapping=fields,
                headless=False,  # Set to True to run in headless mode
                timeout=30000,    # 30 second timeout
                upload_dir=str(upload_dir.absolute()),  # Directory to look for files to upload
            )
            
            if success:
                print("✅ Form filled successfully!")
            else:
                print("❌ Failed to fill the form")
    
    # Clean up
    if sample_file.exists():
        sample_file.unlink()
    
    print("\n🎉 Advanced demo completed!")


if __name__ == "__main__":
    print("Formap Demo - Automated Form Filling")
    print("-" * 80)
    
    # Run the simple example
    asyncio.run(run_simple_example())
    
    # Uncomment to run the advanced example
    # asyncio.run(run_advanced_example())
