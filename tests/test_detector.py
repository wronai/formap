"""Tests for formap form detector."""
import pytest
from pathlib import Path

from formap.services.detector import FormDetector, DetectionOptions
from formap.models.field import FormField, FieldType

SIMPLE_FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Form</title>
</head>
<body>
    <form id="test-form">
        <div class="form-group">
            <label for="name">Full Name</label>
            <input type="text" id="name" name="full_name" required>
        </div>
        
        <div class="form-group">
            <label>
                <input type="email" name="email" placeholder="your@email.com">
                Email Address
            </label>
        </div>
        
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" minlength="8">
        </div>
        
        <div class="form-group">
            <label>Gender</label>
            <input type="radio" id="male" name="gender" value="male">
            <label for="male">Male</label>
            <input type="radio" id="female" name="gender" value="female">
            <label for="female">Female</label>
        </div>
        
        <div class="form-group">
            <label for="country">Country</label>
            <select id="country" name="country">
                <option value="">Select a country</option>
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="resume">Upload Resume</label>
            <input type="file" id="resume" name="resume" accept=".pdf,.doc,.docx">
        </div>
        
        <div class="form-group">
            <label for="message">Your Message</label>
            <textarea id="message" name="message" rows="4"></textarea>
        </div>
        
        <div class="form-actions">
            <button type="submit">Submit</button>
            <button type="reset">Reset</button>
        </div>
    </form>
</body>
</html>
"""

@pytest.mark.asyncio
async def test_detect_form_fields(page):
    """Test detecting form fields from a simple HTML form."""
    # Set up test page
    await page.set_content(SIMPLE_FORM_HTML)
    
    # Initialize detector
    detector = FormDetector(page)
    fields = await detector.detect_form_fields()
    
    # Verify we found the expected number of fields
    assert len(fields) == 9  # 7 inputs + 1 select + 1 textarea
    
    # Convert to dict for easier assertion
    fields_dict = {f.name: f for f in fields}
    
    # Test text input
    assert 'full_name' in fields_dict
    assert fields_dict['full_name'].field_type == FieldType.TEXT
    assert fields_dict['full_name'].label == 'Full Name'
    assert fields_dict['full_name'].required is True
    
    # Test email input with placeholder
    assert 'email' in fields_dict
    assert fields_dict['email'].field_type == FieldType.EMAIL
    assert 'your@email.com' in fields_dict['email'].placeholder
    
    # Test password field
    assert 'password' in fields_dict
    assert fields_dict['password'].field_type == FieldType.PASSWORD
    assert fields_dict['password'].label == 'Password'
    
    # Test radio buttons
    assert 'gender' in fields_dict
    assert fields_dict['gender'].field_type == FieldType.RADIO
    
    # Test select
    assert 'country' in fields_dict
    assert fields_dict['country'].field_type == FieldType.SELECT
    assert len(fields_dict['country'].options) == 3
    assert fields_dict['country'].options[0]['text'] == 'Select a country'
    
    # Test file upload
    assert 'resume' in fields_dict
    assert fields_dict['resume'].field_type == FieldType.FILE
    assert '.pdf,.doc,.docx' in fields_dict['resume'].accept
    
    # Test textarea
    assert 'message' in fields_dict
    assert fields_dict['message'].field_type == FieldType.TEXTAREA

@pytest.mark.asyncio
async def test_xpath_generation(page):
    """Test XPath generation for form elements."""
    html = """
    <form>
        <input id="test1" name="test1">
        <div><input name="test2"></div>
    </form>
    """
    await page.set_content(html)
    
    detector = FormDetector(page)
    fields = await detector.detect_form_fields()
    
    assert len(fields) == 2
    assert fields[0].xpath == '//*[@id="test1"]'  # Should use ID for XPath
    assert '//input[' in fields[1].xpath  # Should generate XPath based on position

@pytest.mark.asyncio
async def test_skip_hidden_fields(page):
    """Test that hidden fields are skipped."""
    html = """
    <form>
        <input type="text" name="visible">
        <input type="hidden" name="hidden_field">
        <input type="text" name="invisible" style="display: none;">
    </form>
    """
    await page.set_content(html)
    
    detector = FormDetector(page)
    fields = await detector.detect_form_fields()
    
    assert len(fields) == 1
    assert fields[0].name == 'visible'

@pytest.mark.asyncio
async def test_duplicate_detection(page):
    """Test that duplicate fields are not processed multiple times."""
    html = """
    <form>
        <input type="text" name="duplicate">
        <input type="text" name="duplicate">
        <input type="text" name="unique">
    </form>
    """
    await page.set_content(html)
    
    detector = FormDetector(page)
    fields = await detector.detect_form_fields()
    
    # Should only have 2 unique fields
    assert len(fields) == 2
    names = {f.name for f in fields}
    assert 'duplicate' in names
    assert 'unique' in names

@pytest.mark.asyncio
async def test_complex_form(page):
    """Test detection with a more complex form structure."""
    html = """
    <form>
        <fieldset>
            <legend>Personal Information</legend>
            <div>
                <label for="first">First Name</label>
                <input type="text" id="first" name="first_name" required>
            </div>
            <div>
                <label for="last">Last Name</label>
                <input type="text" id="last" name="last_name" required>
            </div>
        </fieldset>
        
        <fieldset>
            <legend>Preferences</legend>
            <div>
                <input type="checkbox" id="newsletter" name="newsletter" checked>
                <label for="newsletter">Subscribe to newsletter</label>
            </div>
            <div>
                <label>Notification Method</label>
                <div>
                    <input type="radio" id="email_notif" name="notification" value="email" checked>
                    <label for="email_notif">Email</label>
                    
                    <input type="radio" id="sms_notif" name="notification" value="sms">
                    <label for="sms_notif">SMS</label>
                </div>
            </div>
        </fieldset>
        
        <div>
            <button type="submit">Save</button>
        </div>
    </form>
    """
    await page.set_content(html)
    
    detector = FormDetector(page)
    fields = await detector.detect_form_fields()
    
    assert len(fields) == 5  # first_name, last_name, newsletter, notification (2 radios)
    
    fields_dict = {f.name: f for f in fields}
    assert fields_dict['first_name'].label == 'First Name'
    assert fields_dict['newsletter'].field_type == FieldType.CHECKBOX
    assert fields_dict['notification'].field_type == FieldType.RADIO
    assert fields_dict['notification'].value == 'email'  # Should have checked value