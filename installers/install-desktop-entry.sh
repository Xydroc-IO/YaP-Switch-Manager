#!/bin/bash
# Install desktop entry for YaP Switch Manager

# Get the directory where this script is located (installers/)
INSTALLER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (yap_switch_manager/)
PROJECT_DIR="$(dirname "$INSTALLER_DIR")"

DESKTOP_FILE="$PROJECT_DIR/yap-switch-manager.desktop"
DESKTOP_DIR="$HOME/.local/share/applications"
TARGET_FILE="$DESKTOP_DIR/yap-switch-manager.desktop"

# Find icon path (try multiple locations)
ICON_PATH=""
if [ -f "$(dirname "$PROJECT_DIR")/yaplab.png" ]; then
    ICON_PATH="$(dirname "$PROJECT_DIR")/yaplab.png"
elif [ -f "$PROJECT_DIR/icon.png" ]; then
    ICON_PATH="$PROJECT_DIR/icon.png"
else
    # Use a generic icon or system icon
    ICON_PATH="applications-internet"
fi

# Create applications directory if it doesn't exist
mkdir -p "$DESKTOP_DIR"

# Update the desktop file with the correct paths
sed "s|@EXEC_DIR@|$PROJECT_DIR|g; s|@ICON_PATH@|$ICON_PATH|g; s|Exec=start-switch-manager.sh|Exec=$PROJECT_DIR/launchers/start-switch-manager.sh|g" "$DESKTOP_FILE" > "$TARGET_FILE"

# Make it executable
chmod +x "$TARGET_FILE"

echo "✅ Desktop entry installed to $TARGET_FILE"
echo "   You can now find 'YaP Switch Manager' in your application menu"

