"""Main entry point for the formap package."""
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from playwright.async_api import async_playwright

from .form_detector import FormDetector, FormField
from .logger import log, setup_logger

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def cli(ctx, debug: bool, output: Optional[str]):
    """Formap - Automated form mapping and filling tool."""
    # Set up logging
    log_level = 'DEBUG' if debug else 'INFO'
    setup_logger(log_level)
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['output'] = output

@cli.command()
@click.argument('url')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
@click.option('--timeout', default=30000, help='Page load timeout in milliseconds')
@click.pass_context
async def detect(ctx, url: str, headless: bool, timeout: int):
    """Detect form fields on a web page."""
    output_file = ctx.obj.get('output')
    
    log.info(f"Starting form detection on {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the page
            log.info(f"Navigating to {url}")
            await page.goto(url, timeout=timeout, wait_until='networkidle')
            
            # Handle cookie consent if present
            await handle_cookie_consent(page)
            
            # Detect form fields
            detector = FormDetector(page)
            fields = await detector.detect_form_fields()
            
            # Convert fields to dict
            fields_data = [field.to_dict() for field in fields]
            
            # Output results
            output = {
                'url': url,
                'fields': fields_data,
                'field_count': len(fields_data)
            }
            
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                log.info(f"Saved {len(fields_data)} fields to {output_file}")
            else:
                print(json.dumps(output, indent=2))
                
        except Exception as e:
            log.error(f"Error during form detection: {e}", exc_info=True)
            sys.exit(1)
            
        finally:
            if not headless:
                # Keep browser open if not in headless mode
                log.info("Press Enter to close the browser...")
                input()
            await browser.close()

async def handle_cookie_consent(page):
    """Handle cookie consent popups if present."""
    cookie_selectors = [
        'button#onetrust-accept-btn-handler',
        'button[aria-label*="cookie" i], button[class*="cookie" i]',
        'button:has-text("Accept")',
        'button:has-text("Akzeptieren")',
        'button:has-text("Zustimmen")',
        'button:has-text("Agree")',
        'button:has-text("Accept All")',
        'button:has-text("Accept all")'
    ]
    
    for selector in cookie_selectors:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible() and await element.is_enabled():
                await element.click()
                log.info(f"Clicked cookie consent button: {selector}")
                await asyncio.sleep(1)  # Wait for any animations
                break
        except Exception as e:
            log.debug(f"Error clicking cookie button {selector}: {e}")

def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
