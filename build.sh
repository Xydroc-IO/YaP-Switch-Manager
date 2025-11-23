#!/bin/bash
#
# Build Script for YaP Switch Manager AppImage
# Works on all Linux distributions including Arch, Manjaro, and all desktop environments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="${1:-1.0.0}"
APP_NAME="YaP-Switch-Manager"

echo "🚀 Building YaP Switch Manager v${VERSION}"
echo "=========================================="
echo ""

# Function to build AppImage
build_appimage() {
    APP_DIR="AppDir"
    BUILD_DIR="build"
    
    echo "🧹 Cleaning previous builds..."
    rm -rf "$APP_DIR" "$BUILD_DIR" "${APP_NAME}-${VERSION}.AppImage" dist/ build/ *.spec
    mkdir -p "$BUILD_DIR"
    
    # Check for required tools
    echo "🔍 Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Error: python3 not found"
        exit 1
    fi
    
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        echo "⚠️  PyInstaller not found. Installing..."
        python3 -m pip install pyinstaller --user
    fi
    
    # Create AppDir structure
    echo "📁 Creating AppDir structure..."
    mkdir -p "$APP_DIR/usr/bin"
    mkdir -p "$APP_DIR/usr/share/applications"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/512x512/apps"
    
    # Copy icon
    echo "🎨 Copying icons..."
    if [ -f "icon.png" ]; then
        cp icon.png "$APP_DIR/usr/share/icons/hicolor/256x256/apps/yap-switch-manager.png"
        cp icon.png "$APP_DIR/usr/share/icons/hicolor/512x512/apps/yap-switch-manager.png"
        cp icon.png "$APP_DIR/yap-switch-manager.png"
        ICON_FILE="icon.png"
    else
        echo "⚠️  Warning: No icon found, using default"
        ICON_FILE=""
    fi
    
    # Create desktop file
    echo "📝 Creating desktop file..."
    cat > "$APP_DIR/yap-switch-manager.desktop" << EOF
[Desktop Entry]
Type=Application
Name=YaP Switch Manager
GenericName=Network Switch Manager
Comment=Manage network switch via web console
Exec=yap-switch-manager
Icon=yap-switch-manager
Categories=Network;System;Utility;
Keywords=switch;network;management;console;
Terminal=false
StartupNotify=true
EOF
    
    cp "$APP_DIR/yap-switch-manager.desktop" "$APP_DIR/usr/share/applications/yap-switch-manager.desktop"
    
    # Build with PyInstaller
    echo "🔨 Building with PyInstaller..."
    cd "$SCRIPT_DIR"
    
    ICON_ARG=""
    if [ -n "$ICON_FILE" ] && [ -f "$ICON_FILE" ]; then
        ICON_ARG="icon='$ICON_FILE',"
    fi
    
    cat > yap_switch_manager.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['core/switch_manager.py'],
    pathex=['$SCRIPT_DIR'],
    binaries=[],
    datas=[
        ('icon.png', '.'),
        ('core/webview_launcher.py', 'core'),
    ],
    hiddenimports=[
        'webview',
        'requests',
        'PIL',
        'PIL._tkinter_finder',
        'pystray',
        'pystray._x11',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'urllib3.util.retry',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='yap-switch-manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    $ICON_ARG
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='yap-switch-manager',
)
EOF
    
    # Run PyInstaller
    echo "🔨 Running PyInstaller..."
    python3 -m PyInstaller yap_switch_manager.spec --clean --noconfirm
    
    # Copy built executable to AppDir (onedir mode)
    echo "📦 Copying files to AppDir..."
    if [ -d "dist/yap-switch-manager" ]; then
        # onedir mode - copy entire directory
        cp -r dist/yap-switch-manager/* "$APP_DIR/usr/bin/"
        chmod +x "$APP_DIR/usr/bin/yap-switch-manager"
    elif [ -f "dist/yap-switch-manager" ]; then
        # onefile mode fallback
        cp dist/yap-switch-manager "$APP_DIR/usr/bin/"
        chmod +x "$APP_DIR/usr/bin/yap-switch-manager"
    else
        echo "❌ Error: Built executable not found"
        exit 1
    fi
    
    # Copy webview_launcher.py
    if [ -f "core/webview_launcher.py" ]; then
        mkdir -p "$APP_DIR/core"
        cp core/webview_launcher.py "$APP_DIR/core/"
        cp core/webview_launcher.py "$APP_DIR/usr/bin/"
    fi
    
    if [ -f "icon.png" ]; then
        cp icon.png "$APP_DIR/"
    fi
    
    # Create AppRun script
    echo "📜 Creating AppRun..."
    cat > "$APP_DIR/AppRun" << 'APPRUN_EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export APPDIR="${HERE}"

cd "${HERE}"

if [ -f "${HERE}/core/webview_launcher.py" ]; then
    export PYTHONPATH="${HERE}:${HERE}/core:${PYTHONPATH}"
elif [ -f "${HERE}/usr/bin/webview_launcher.py" ]; then
    export PYTHONPATH="${HERE}/usr/bin:${PYTHONPATH}"
fi

exec "${HERE}/usr/bin/yap-switch-manager" "$@"
APPRUN_EOF
    chmod +x "$APP_DIR/AppRun"
    
    # Create AppImage
    echo "📦 Creating AppImage..."
    
    if command -v appimagetool &> /dev/null; then
        echo "✅ Using appimagetool..."
        appimagetool "$APP_DIR" "${APP_NAME}-${VERSION}.AppImage"
    elif command -v wget &> /dev/null || command -v curl &> /dev/null; then
        echo "📥 Downloading appimagetool..."
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        elif [ "$ARCH" = "aarch64" ]; then
            APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage"
        else
            echo "❌ Unsupported architecture: $ARCH"
            exit 1
        fi
        
        if command -v wget &> /dev/null; then
            wget -q "$APPIMAGETOOL_URL" -O appimagetool.AppImage
        else
            curl -L "$APPIMAGETOOL_URL" -o appimagetool.AppImage
        fi
        
        chmod +x appimagetool.AppImage
        ./appimagetool.AppImage "$APP_DIR" "${APP_NAME}-${VERSION}.AppImage"
        rm -f appimagetool.AppImage
    else
        echo "⚠️  appimagetool not found and cannot download."
        echo "   Please install appimagetool or download it manually:"
        echo "   https://github.com/AppImage/AppImageKit/releases"
        exit 1
    fi
    
    chmod +x "${APP_NAME}-${VERSION}.AppImage"
    
    echo ""
    echo "✅ AppImage built successfully!"
    echo "📦 Output: ${APP_NAME}-${VERSION}.AppImage"
    echo ""
}

# Build AppImage
build_appimage

echo "=========================================="
echo "✅ Build complete!"
echo "=========================================="
echo ""
if [ -f "${APP_NAME}-${VERSION}.AppImage" ]; then
    echo "📦 Built: ${APP_NAME}-${VERSION}.AppImage"
fi
echo ""

