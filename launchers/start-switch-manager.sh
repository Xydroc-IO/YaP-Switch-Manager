#!/bin/bash
# YaP Switch Manager Launcher Script
# This script launches the YaP Switch Manager application

# Get the directory where this script is located (launchers/)
LAUNCHER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (project root)
SCRIPT_DIR="$(dirname "$LAUNCHER_DIR")"

# Change to the project root directory
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  Warning: $1${NC}"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    print_error "Python 3.7 or higher is required (found Python $PYTHON_VERSION)"
    exit 1
fi

print_success "Python $PYTHON_VERSION detected"

# Check if required packages are installed
MISSING_PACKAGES=()

python3 -c "import webview" 2>/dev/null
if [ $? -ne 0 ]; then
    MISSING_PACKAGES+=("pywebview")
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    MISSING_PACKAGES+=("requests")
fi

python3 -c "import PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    MISSING_PACKAGES+=("Pillow")
fi

# If packages are missing, offer to install them
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_warning "Missing required packages: ${MISSING_PACKAGES[*]}"
    echo ""
    echo "Would you like to install dependencies now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        if [ -f "$SCRIPT_DIR/installers/install-dependencies.sh" ]; then
            echo "Running dependency installer..."
            bash "$SCRIPT_DIR/installers/install-dependencies.sh"
            # Check again after installation
            python3 -c "import webview" 2>/dev/null
            if [ $? -ne 0 ]; then
                print_error "Failed to install dependencies. Please run installers/install-dependencies.sh manually."
                exit 1
            fi
        else
            print_error "installers/install-dependencies.sh not found. Please install dependencies manually:"
            echo "  pip install pywebview requests Pillow"
            exit 1
        fi
    else
        print_error "Cannot run without required packages. Exiting."
        exit 1
    fi
fi

# Check if switch_manager.py exists in core folder
if [ ! -f "$SCRIPT_DIR/core/switch_manager.py" ]; then
    print_error "core/switch_manager.py not found in $SCRIPT_DIR"
    exit 1
fi

# Run the application
print_success "Starting YaP Switch Manager..."
echo ""
python3 "$SCRIPT_DIR/core/switch_manager.py"

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    print_error "Application exited with error code: $EXIT_CODE"
    exit $EXIT_CODE
fi
