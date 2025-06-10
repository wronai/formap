#!/bin/bash
# Script to install system dependencies for Playwright

echo "Installing system dependencies for Playwright..."

# For Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y \
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
        libxcb-dri3-0 \
        libxcb1 \
        libxshmfence1 \
        libxcb-icccm4 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-xfixes0 \
        libxcb-xinerama0 \
        libxcb-xtest0 \
        libxcb-shm0 \
        libxcb-dri3-0 \
        libxcb-present0 \
        libxcb-sync1 \
        libxss1 \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
        libgconf-2-4 \
        libdbus-1-3 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxi6 \
        libxtst6 \
        libnss3 \
        libcups2 \
        libxss1 \
        libxrandr2 \
        libasound2 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libpangocairo-1.0-0 \
        libgtk-3-0 \
        libgbm1 \
        libxshmfence1 \
        libxcb-dri3-0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libatspi2.0-0 \
        libx11-xcb1 \
        libxcb1 \
        libxcb-dri3-0 \
        libxcb-shm0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-xfixes0 \
        libxcb-xinerama0 \
        libxcb-xtest0 \
        libxcb-present0 \
        libxcb-sync1 \
        libxss1 \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libgtk-3-0 \
        libgconf-2-4 \
        libdbus-1-3 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxi6 \
        libxtst6 \
        libnss3 \
        libcups2 \
        libxss1 \
        libxrandr2 \
        libasound2 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libpangocairo-1.0-0 \
        libgtk-3-0

# For Fedora
elif command -v dnf &> /dev/null; then
    sudo dnf install -y \
        alsa-lib.x86_64 \
        atk.x86_64 \
        cups-libs.x86_64 \
        gtk3.x86_64 \
        ipa-gothic-fonts \
        libXcomposite.x86_64 \
        libXcursor.x86_64 \
        libXdamage.x86_64 \
        libXext.x86_64 \
        libXi.x86_64 \
        libXrandr.x86_64 \
        libXScrnSaver.x86_64 \
        libXtst.x86_64 \
        pango.x86_64 \
        xorg-x11-fonts-100dpi \
        xorg-x11-fonts-75dpi \
        xorg-x11-fonts-cyrillic \
        xorg-x11-fonts-misc \
        xorg-x11-fonts-Type1 \
        xorg-x11-utils \
        at-spi2-atk \
        libxkbcommon \
        libxshmfence \
        libX11-xcb \
        libXcomposite \
        libXdamage \
        libXfixes \
        libXrandr \
        libgbm \
        pango \
        cairo \
        gdk-pixbuf2 \
        gtk3 \
        libdrm \
        libXcursor \
        libXxf86vm \
        libxcb

# For Arch Linux
elif command -v pacman &> /dev/null; then
    sudo pacman -S --needed \
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
else
    echo "Unsupported package manager. Please install dependencies manually."
    exit 1
fi

echo -e "\n✅ System dependencies installed. Please run the setup script again:"
echo -e "source venv/bin/activate"
echo -e "./setup_env.sh"
