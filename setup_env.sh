#!/bin/bash
# Simple setup script for FORMAP

echo "Setting up FORMAP environment..."

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv --clear

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r form-mapper/requirements.txt

# Install Playwright
echo "Installing Playwright..."
pip install playwright
playwright install

# Install browsers
echo "Installing Playwright browsers..."
python -m playwright install

# Make scripts executable
chmod +x form-mapper/*.py
chmod +x form-mapper/*.sh

echo -e "\n✅ Setup complete!"
echo -e "\nTo activate the virtual environment, run:"
echo -e "  source venv/bin/activate"
echo -e "\nTo deactivate the virtual environment, run:"
echo -e "  deactivate"

# Run the application
echo -e "\n🚀 To map a form, run:"
echo -e "./form-mapper/map_fields.py https://example.com/form"

echo -e "\n🔧 To fill a form, first create a mapping, then run:"
echo -e "./form-mapper/fill_form.py form_map.json"
