#!/bin/bash
# Universal installer for FORMAP on Linux
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if script is run as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root is not recommended. Please run as a regular user.${NC}"
    exit 1
fi

# Function to detect Linux distribution
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    # Convert to lowercase
    OS=$(echo "$OS" | tr '[:upper:]' '[:lower:]')
    
    echo "Detected OS: $OS $VER"
}

# Function to install dependencies
install_dependencies() {
    echo -e "${GREEN}Installing system dependencies...${NC}"
    
    case "$OS" in
        ubuntu|debian|linuxmint|pop|elementary|kali|parrot)
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-venv \
                python3-pip \
                python3-wheel \
                python3-setuptools \
                libnss3 \
                libnspr4 \
                libatk1.0-0 \
                libatk-bridge2.0-0 \
                libcups2 \
                libdrm2 \
                libxkbcommon0 \
                libxcomposite1 \
                libxdamage1 \
                libxfixes3 \
                libxrandr2 \
                libgbm1 \
                libasound2 \
                libatspi2.0-0 \
                libx11-xcb1 \
                libxcb1
            ;;
            
        fedora|centos|rhel|amzn|ol|rocky|almalinux)
            if command -v dnf &> /dev/null; then
                sudo dnf install -y \
                    python3 \
                    python3-venv \
                    python3-pip \
                    python3-wheel \
                    python3-setuptools \
                    alsa-lib \
                    atk \
                    at-spi2-atk \
                    cairo \
                    cups-libs \
                    gtk3 \
                    ipa-gothic-fonts \
                    libXcomposite \
                    libXcursor \
                    libXdamage \
                    libXext \
                    libXi \
                    libXrandr \
                    libXScrnSaver \
                    libXtst \
                    pango \
                    xorg-x11-fonts-100dpi \
                    xorg-x11-fonts-75dpi \
                    xorg-x11-fonts-cyrillic \
                    xorg-x11-fonts-misc \
                    xorg-x11-fonts-Type1 \
                    xorg-x11-utils
            elif command -v yum &> /dev/null; then
                sudo yum install -y \
                    python3 \
                    python3-venv \
                    python3-pip \
                    python3-wheel \
                    python3-setuptools \
                    alsa-lib \
                    atk \
                    at-spi2-atk \
                    cairo \
                    cups-libs \
                    gtk3 \
                    ipa-gothic-fonts \
                    libXcomposite \
                    libXcursor \
                    libXdamage \
                    libXext \
                    libXi \
                    libXrandr \
                    libXScrnSaver \
                    libXtst \
                    pango \
                    xorg-x11-fonts-100dpi \
                    xorg-x11-fonts-75dpi \
                    xorg-x11-fonts-cyrillic \
                    xorg-x11-fonts-misc \
                    xorg-x11-fonts-Type1 \
                    xorg-x11-utils
            fi
            ;;
            
        arch|manjaro|endeavouros|garuda)
            sudo pacman -S --needed \
                python \
                python-pip \
                python-wheel \
                python-setuptools \
                alsa-lib \
                atk \
                at-spi2-atk \
                cairo \
                cups \
                gdk-pixbuf2 \
                glib2 \
                gtk3 \
                libdrm \
                libxcb \
                libxkbcommon \
                libxshmfence \
                libx11 \
                libxcomposite \
                libxdamage \
                libxext \
                libxfixes \
                libxrandr \
                mesa \
                nss \
                pango \
                xdg-utils
            ;;
            
        opensuse*|suse*|sles*)
            sudo zypper install -y \
                python3 \
                python3-venv \
                python3-pip \
                python3-wheel \
                python3-setuptools \
                alsa \
                atk \
                at-spi2-atk \
                cairo \
                cups \
                gtk3 \
                libXss1 \
                libXcomposite1 \
                libXcursor1 \
                libXdamage1 \
                libXext6 \
                libXi6 \
                libXrandr2 \
                libXScrnSaver1 \
                libXtst6 \
                pango \
                xdg-utils
            ;;
            
        *)
            echo -e "${YELLOW}Unsupported Linux distribution. Trying to install with common packages...${NC}"
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y \
                    python3 \
                    python3-venv \
                    python3-pip \
                    python3-wheel \
                    python3-setuptools
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y \
                    python3 \
                    python3-venv \
                    python3-pip \
                    python3-wheel \
                    python3-setuptools
            elif command -v yum &> /dev/null; then
                sudo yum install -y \
                    python3 \
                    python3-venv \
                    python3-pip \
                    python3-wheel \
                    python3-setuptools
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --needed \
                    python \
                    python-pip \
                    python-wheel \
                    python-setuptools
            fi
            ;;
    esac
    
    echo -e "${GREEN}System dependencies installed.${NC}"
}

# Function to setup Python virtual environment
setup_python_env() {
    echo -e "${GREEN}Setting up Python virtual environment...${NC}"
    
    # Remove existing virtual environment if it exists
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf venv
    fi
    
    # Create new virtual environment
    python3 -m venv venv --clear
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    pip install -r form-mapper/requirements.txt
    
    # Install Playwright
    echo -e "${GREEN}Installing Playwright...${NC}"
    pip install playwright
    
    # Install browsers
    echo -e "${GREEN}Installing Playwright browsers...${NC}"
    python -m playwright install
    
    echo -e "${GREEN}✅ Python environment setup complete!${NC}"
}

# Function to create desktop entry
create_desktop_entry() {
    echo -e "${GREEN}Creating desktop entry...${NC}"
    
    DESKTOP_FILE="$HOME/.local/share/applications/formap.desktop"
    EXEC_PATH="$(pwd)/venv/bin/python $(pwd)/form-mapper/map_fields.py"
    ICON_PATH="$(pwd)/form-mapper/icon.png"
    
    # Create icon directory if it doesn't exist
    mkdir -p "$(pwd)/form-mapper"
    
    # Download icon if it doesn't exist
    if [ ! -f "$ICON_PATH" ]; then
        wget -q https://raw.githubusercontent.com/yourusername/formap/main/form-mapper/icon.png -O "$ICON_PATH" || true
    fi
    
    # Create desktop entry
    cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=FORMAP
Comment=Form Mapper & Auto-Filler
Exec=$EXEC_PATH %u
Icon=$ICON_PATH
Terminal=true
Categories=Development;Utility;
StartupNotify=true
EOL
    
    # Make desktop entry executable
    chmod +x "$DESKTOP_FILE"
    
    echo -e "${GREEN}✅ Desktop entry created at $DESKTOP_FILE${NC}"
}

# Main script
echo -e "${GREEN}🚀 Starting FORMAP installation...${NC}"

# Detect Linux distribution
detect_linux_distro

# Install system dependencies
install_dependencies

# Setup Python environment
setup_python_env

# Create desktop entry (optional)
read -p "Do you want to create a desktop entry? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_desktop_entry
fi

echo -e "${GREEN}🎉 FORMAP installation complete!${NC}"
echo -e "\nTo get started, run the following commands:"
echo -e "  source venv/bin/activate"
echo -e "  python form-mapper/map_fields.py https://example.com/form"
echo -e "\nOr to fill a form:"
echo -e "  python form-mapper/fill_form.py form_map.json"

exit 0
