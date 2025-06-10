# 🧠 FORMAP - Form Mapper & Auto-Filler

A powerful tool to automatically map and fill web forms using Playwright and Python.

## ✨ Features

- 🔍 Automatically map form fields by tabbing through them
- 💾 Save form field mappings to a JSON file
- 🚀 Automatically fill forms using saved mappings
- 🔒 Support for various form field types (text, select, radio, checkbox, etc.)
- 🛠️ Environment variable support for sensitive data
- 🐳 Docker support for easy deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Playwright browsers
- (Optional) Docker

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/formap.git
   cd formap
   ```

2. Install dependencies:
   ```bash
   pip install -r form-mapper/requirements.txt
   playwright install
   ```

## 🛠️ Usage

### 1. Map Form Fields

To map the fields of a form:

```bash
python form-mapper/map_fields.py <url> [output_file]
```

Example:
```bash
python form-mapper/map_fields.py https://example.com/login form_map.json
```

Follow the on-screen instructions to tab through the form fields. Press 's' to save or 'q' to quit without saving.

### 2. Fill a Form

To fill a form using a saved mapping:

```bash
python form-mapper/fill_form.py [mapping_file]
```

Example:
```bash
python form-mapper/fill_form.py form_map.json
```

### Using Environment Variables

You can pre-fill form fields using environment variables. Create a `.env` file based on `example.env`:

```bash
cp form-mapper/example.env .env
# Edit .env with your values
```

Environment variables should be named `FORM_<FIELD_NAME>` where `<FIELD_NAME>` is the uppercase version of your field's name or label.

## 🐳 Docker Support

Build the Docker image:

```bash
docker-compose -f form-mapper/docker-compose.yml build
```

Run the container:

```bash
docker-compose -f form-mapper/docker-compose.yml up -d
docker-compose -f form-mapper/docker-compose.yml exec formmapper bash
```

Inside the container, you can run the scripts as usual:

```bash
python map_fields.py https://example.com
python fill_form.py form_map.json
```

## 📁 Project Structure

```
form-mapper/
├── Dockerfile           # Docker configuration
├── Makefile            # Common commands
├── README.md           # This file
├── docker-compose.yml  # Docker Compose configuration
├── example.env         # Example environment variables
├── fill_form.py        # Form filling script
├── map_fields.py       # Form field mapping script
└── requirements.txt    # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
