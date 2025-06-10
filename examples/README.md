# Formap Examples

This directory contains example scripts that demonstrate how to use Formap for form automation.

## Prerequisites

1. Install the required dependencies:
   ```bash
   cd /path/to/formap
   pip install -e .  # Install formap in development mode
   pip install -r examples/requirements.txt  # Install example dependencies
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Running the Examples

### Simple Form Filling Example

This example demonstrates basic form detection and filling:

```bash
python examples/demo.py
```

### Advanced Example with File Uploads

To run the advanced example that includes file uploads, uncomment the relevant section in `demo.py` and run:

```bash
python examples/demo.py
```

## Example Form

The example form (`simple_form.html`) is a simple registration form with various field types:

- Text inputs (username, email, password, full name)
- Textarea (bio)
- Select dropdown (country)
- Checkbox (subscribe to newsletter)

## Customizing the Examples

You can modify the example form or create your own form and update the `demo.py` script to work with it. The main components to modify are:

1. The form data in the `FormData` object
2. The field mappings (if your form has different field names)
3. The URL or file path to your form

## Troubleshooting

- If you encounter any issues, make sure all dependencies are installed correctly.
- Enable debug logging by setting the environment variable `FORMAP_DEBUG=1`.
- Check the browser console for any JavaScript errors.

## Next Steps

- Try running the examples with different form data
- Experiment with different form field types and validation
- Integrate Formap into your own projects
