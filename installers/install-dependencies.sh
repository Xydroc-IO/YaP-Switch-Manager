#!/bin/bash
#
# --- Universal YaP Switch Manager Dependency Installer ---
# This script installs all necessary dependencies for YaP Switch Manager
# Supports all major Linux distributions and desktop environments

# Exit immediately if a command fails (but allow graceful handling for package installs)
set -e

# Function to handle errors gracefully
handle_error() {
    echo "❌ ERROR: $1"
    exit 1
}

# --- Section 0: Setup and Checks ---

# Find the absolute path of the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "🚀 Starting YaP Switch Manager dependency installation..."
echo ""

# Safety Check: Prevent running the whole script as root
if [ "$(id -u)" -eq 0 ]; then
    echo "❌ ERROR: Do not run this script as root or with 'sudo'."
    echo "It will ask for your password with 'sudo' when needed."
    exit 1
fi

# --- Section 1: Dependency Installation ---

# 1. Detect the package manager (supporting all major Linux distributions)
if command -v apt &> /dev/null; then
    PACKAGE_MANAGER="apt"
    DISTRO_FAMILY="debian"
elif command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
    DISTRO_FAMILY="redhat"
elif command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
    DISTRO_FAMILY="redhat"
elif command -v pacman &> /dev/null; then
    PACKAGE_MANAGER="pacman"
    DISTRO_FAMILY="arch"
elif command -v zypper &> /dev/null; then
    PACKAGE_MANAGER="zypper"
    DISTRO_FAMILY="suse"
elif command -v apk &> /dev/null; then
    PACKAGE_MANAGER="apk"
    DISTRO_FAMILY="alpine"
elif command -v eopkg &> /dev/null; then
    PACKAGE_MANAGER="eopkg"
    DISTRO_FAMILY="solus"
elif command -v emerge &> /dev/null; then
    PACKAGE_MANAGER="emerge"
    DISTRO_FAMILY="gentoo"
elif command -v nix-env &> /dev/null; then
    PACKAGE_MANAGER="nix"
    DISTRO_FAMILY="nixos"
elif command -v guix &> /dev/null; then
    PACKAGE_MANAGER="guix"
    DISTRO_FAMILY="guix"
elif command -v xbps-install &> /dev/null; then
    PACKAGE_MANAGER="xbps"
    DISTRO_FAMILY="void"
else
    echo "❌ ERROR: Could not detect a supported package manager."
    echo "Supported managers: apt (Debian/Ubuntu), dnf/yum (Fedora/RHEL), pacman (Arch/Manjaro), zypper (openSUSE), apk (Alpine), eopkg (Solus), emerge (Gentoo), nix (NixOS), guix (GuixSD), xbps (Void)"
    exit 1
fi

echo "✅ Detected package manager: $PACKAGE_MANAGER"
echo "✅ Detected distribution family: $DISTRO_FAMILY"
echo ""

# 2. Detect desktop environment (comprehensive detection)
DETECT_DE=""
if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    DE_STRING=$(echo "$XDG_CURRENT_DESKTOP" | tr '[:upper:]' '[:lower:]')
    if echo "$DE_STRING" | grep -qi "kde\|plasma"; then
        DETECT_DE="kde"
    elif echo "$DE_STRING" | grep -qi "gnome"; then
        DETECT_DE="gnome"
    elif echo "$DE_STRING" | grep -qi "xfce"; then
        DETECT_DE="xfce"
    elif echo "$DE_STRING" | grep -qi "cinnamon"; then
        DETECT_DE="cinnamon"
    elif echo "$DE_STRING" | grep -qi "lxde\|lxqt"; then
        DETECT_DE="lxde"
    elif echo "$DE_STRING" | grep -qi "mate"; then
        DETECT_DE="mate"
    elif echo "$DE_STRING" | grep -qi "budgie"; then
        DETECT_DE="budgie"
    elif echo "$DE_STRING" | grep -qi "pantheon"; then
        DETECT_DE="pantheon"
    elif echo "$DE_STRING" | grep -qi "deepin"; then
        DETECT_DE="deepin"
    else
        DETECT_DE="gtk"
    fi
elif [ -n "$DESKTOP_SESSION" ]; then
    SESSION_STRING=$(echo "$DESKTOP_SESSION" | tr '[:upper:]' '[:lower:]')
    if echo "$SESSION_STRING" | grep -qi "kde\|plasma"; then
        DETECT_DE="kde"
    elif echo "$SESSION_STRING" | grep -qi "gnome"; then
        DETECT_DE="gnome"
    elif echo "$SESSION_STRING" | grep -qi "xfce"; then
        DETECT_DE="xfce"
    elif echo "$SESSION_STRING" | grep -qi "cinnamon"; then
        DETECT_DE="cinnamon"
    elif echo "$SESSION_STRING" | grep -qi "mate"; then
        DETECT_DE="mate"
    elif echo "$SESSION_STRING" | grep -qi "lxde\|lxqt"; then
        DETECT_DE="lxde"
    else
        DETECT_DE="gtk"
    fi
elif [ -n "$XDG_SESSION_DESKTOP" ]; then
    SESSION_STRING=$(echo "$XDG_SESSION_DESKTOP" | tr '[:upper:]' '[:lower:]')
    if echo "$SESSION_STRING" | grep -qi "kde\|plasma"; then
        DETECT_DE="kde"
    elif echo "$SESSION_STRING" | grep -qi "gnome"; then
        DETECT_DE="gnome"
    elif echo "$SESSION_STRING" | grep -qi "xfce"; then
        DETECT_DE="xfce"
    elif echo "$SESSION_STRING" | grep -qi "cinnamon"; then
        DETECT_DE="cinnamon"
    elif echo "$SESSION_STRING" | grep -qi "mate"; then
        DETECT_DE="mate"
    else
        DETECT_DE="gtk"
    fi
else
    DETECT_DE="gtk"
fi

echo "✅ Detected desktop environment: $DETECT_DE"
echo ""

# 3. Update package lists
echo "🔄 Updating package lists..."
if [ "$PACKAGE_MANAGER" == "apt" ]; then
    sudo apt update
elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
    # dnf check-update exits 100 if updates are available, which is not an error.
    sudo dnf check-update || [[ $? -eq 100 ]]
elif [ "$PACKAGE_MANAGER" == "yum" ]; then
    sudo yum check-update || [[ $? -eq 100 ]]
elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
    sudo pacman -Sy --noconfirm
elif [ "$PACKAGE_MANAGER" == "zypper" ]; then
    sudo zypper refresh
elif [ "$PACKAGE_MANAGER" == "apk" ]; then
    sudo apk update
elif [ "$PACKAGE_MANAGER" == "eopkg" ]; then
    sudo eopkg update-repo
elif [ "$PACKAGE_MANAGER" == "emerge" ]; then
    echo "⚠️  Note: Gentoo users should run 'sudo emerge --sync' manually if needed"
elif [ "$PACKAGE_MANAGER" == "nix" ]; then
    echo "⚠️  Note: NixOS users should use nix-env or nix-shell for package management"
elif [ "$PACKAGE_MANAGER" == "guix" ]; then
    echo "⚠️  Note: GuixSD users should use 'guix package' for package management"
elif [ "$PACKAGE_MANAGER" == "xbps" ]; then
    sudo xbps-install -S
fi

# 4. Define system packages for each distribution
echo "⚙️ Defining system packages..."
echo ""

# Base packages needed for all distributions
if [ "$PACKAGE_MANAGER" == "apt" ]; then
    # For Debian, Ubuntu, Mint, Pop!_OS, Elementary OS, etc.
    SYSTEM_PACKAGES="python3 python3-pip python3-tk python3-dev"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libwebkit2gtk-4.0-dev libgtk-3-dev"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-dev zlib1g-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev"
    INSTALL_CMD="sudo apt install -y"
elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
    # For Fedora, CentOS Stream, RHEL 8+
    SYSTEM_PACKAGES="python3 python3-pip python3-tkinter python3-devel"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk3-devel gtk3-devel"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel"
    INSTALL_CMD="sudo dnf install -y"
elif [ "$PACKAGE_MANAGER" == "yum" ]; then
    # For CentOS 7, RHEL 7, older Fedora
    SYSTEM_PACKAGES="python3 python3-pip python3-tkinter python3-devel"
    # WebKitGTK for pywebview (may need EPEL repository)
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkitgtk3-devel gtk3-devel"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel"
    INSTALL_CMD="sudo yum install -y"
elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
    # For Arch Linux, Manjaro, EndeavourOS, Garuda, etc.
    SYSTEM_PACKAGES="python python-pip python-tkinter"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk"
    # Additional dependencies for Pillow (usually included in python-pillow but listed for completeness)
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-turbo zlib libtiff freetype2 lcms2 libwebp"
    INSTALL_CMD="sudo pacman -S --noconfirm"
elif [ "$PACKAGE_MANAGER" == "zypper" ]; then
    # For openSUSE, SUSE Linux Enterprise
    SYSTEM_PACKAGES="python3 python3-pip python3-tk python3-devel"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk3-devel gtk3-devel"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg8-devel zlib-devel libtiff-devel freetype2-devel lcms2-devel libwebp-devel"
    INSTALL_CMD="sudo zypper install -y"
elif [ "$PACKAGE_MANAGER" == "apk" ]; then
    # For Alpine Linux
    SYSTEM_PACKAGES="python3 py3-pip py3-tkinter"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk-dev gtk+3.0-dev"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES jpeg-dev zlib-dev tiff-dev freetype-dev lcms2-dev libwebp-dev"
    INSTALL_CMD="sudo apk add"
elif [ "$PACKAGE_MANAGER" == "eopkg" ]; then
    # For Solus
    SYSTEM_PACKAGES="python3 python3-pip python3-tkinter"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk-devel gtk3-devel"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel"
    INSTALL_CMD="sudo eopkg install -y"
elif [ "$PACKAGE_MANAGER" == "emerge" ]; then
    # For Gentoo
    echo "⚠️  Gentoo users: Please install the following packages manually:"
    echo "   dev-lang/python:3"
    echo "   dev-python/pip"
    echo "   dev-python/pywebview"
    echo "   net-libs/webkit-gtk"
    echo "   dev-python/Pillow"
    echo ""
    echo "   Example: sudo emerge -av dev-lang/python:3 dev-python/pip net-libs/webkit-gtk dev-python/pywebview dev-python/Pillow"
    echo ""
    read -p "Press Enter to continue with pip installation only, or Ctrl+C to exit..."
    INSTALL_CMD=""
    SYSTEM_PACKAGES=""
elif [ "$PACKAGE_MANAGER" == "nix" ]; then
    # For NixOS
    echo "⚠️  NixOS users: Please install packages using nix-env or add to configuration.nix"
    echo "   nix-env -i python3 python3Packages.pip python3Packages.pywebview python3Packages.Pillow"
    echo ""
    read -p "Press Enter to continue with pip installation only, or Ctrl+C to exit..."
    INSTALL_CMD=""
    SYSTEM_PACKAGES=""
elif [ "$PACKAGE_MANAGER" == "guix" ]; then
    # For GuixSD
    echo "⚠️  GuixSD users: Please install packages using guix package"
    echo "   guix package -i python python-pip python-pywebview python-pillow"
    echo ""
    read -p "Press Enter to continue with pip installation only, or Ctrl+C to exit..."
    INSTALL_CMD=""
    SYSTEM_PACKAGES=""
elif [ "$PACKAGE_MANAGER" == "xbps" ]; then
    # For Void Linux
    SYSTEM_PACKAGES="python3 python3-pip python3-tkinter"
    # WebKitGTK for pywebview
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES webkit2gtk-devel gtk+3-devel"
    # Additional dependencies for Pillow
    SYSTEM_PACKAGES="$SYSTEM_PACKAGES libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel"
    INSTALL_CMD="sudo xbps-install -y"
fi

# 5. Install system dependencies
if [ -n "$SYSTEM_PACKAGES" ]; then
    echo "📦 Installing system packages..."
    echo "   Packages: $SYSTEM_PACKAGES"
    echo ""
    set +e  # Temporarily disable exit on error for package installation
    $INSTALL_CMD $SYSTEM_PACKAGES
    INSTALL_EXIT_CODE=$?
    set -e  # Re-enable exit on error
    if [ $INSTALL_EXIT_CODE -ne 0 ]; then
        echo "⚠️  WARNING: Some system packages may have failed to install (exit code: $INSTALL_EXIT_CODE)."
        echo "   Continuing anyway - you may need to install missing packages manually..."
        echo ""
    else
        echo "✅ System packages installed successfully!"
        echo ""
    fi
fi

# 6. Upgrade pip first (important for compatibility)
echo "🔄 Upgrading pip..."
python3 -m pip install --upgrade pip --break-system-packages 2>/dev/null || \
python3 -m pip install --upgrade pip --user 2>/dev/null || \
python3 -m pip install --upgrade pip 2>/dev/null || \
echo "⚠️  Could not upgrade pip, continuing with existing version..."
echo ""

# 7. Install Python packages via pip
echo "🐍 Installing Python packages via pip..."
echo ""

# Determine if we need --break-system-packages flag (Python 3.11+)
PIP_FLAGS=""
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    PIP_FLAGS="--break-system-packages"
fi

# Function to install pip package with error handling
install_pip_package() {
    set +e  # Temporarily disable exit on error
    local package_name="$1"
    local package_spec="${2:-$package_name}"
    echo "   --> Installing $package_name..."
    if [ -n "$PIP_FLAGS" ]; then
        if ! python3 -m pip install "$package_spec" $PIP_FLAGS; then
            echo "   ⚠️  WARNING: Failed to install $package_name with system packages flag, trying user install..."
            if ! python3 -m pip install "$package_spec" --user; then
                echo "   ❌ ERROR: Failed to install $package_name"
                set -e  # Re-enable exit on error
                return 1
            fi
        fi
    else
        if ! python3 -m pip install "$package_spec" --user; then
            echo "   ❌ ERROR: Failed to install $package_name"
            set -e  # Re-enable exit on error
            return 1
        fi
    fi
    set -e  # Re-enable exit on error
    return 0
}

# Install required Python packages
echo "📦 Installing core dependencies..."
install_pip_package "pywebview" "pywebview>=4.0.0"
install_pip_package "requests" "requests>=2.28.0"
install_pip_package "Pillow" "Pillow>=9.0.0"
install_pip_package "pystray" "pystray>=0.19.0"

echo ""
echo "--------------------------------------------------------"
echo "✅ Dependency installation complete!"
echo "--------------------------------------------------------"
echo ""
echo "You can now run YaP Switch Manager with:"
echo "   python3 core/switch_manager.py"
echo "   or"
echo "   ./launchers/start-switch-manager.sh"
echo ""

