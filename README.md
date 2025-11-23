<div align="center">

![YaP Switch Manager](icon.png)

# YaP Switch Manager

A modern, cross-platform desktop application to manage your network switch via its web console. Features a clean, intuitive interface with embedded webview support, system tray integration, and comprehensive multi-monitor support.

</div>

## Features

- **Embedded Console**: Open the switch web console in an embedded window within the application
- **External Browser**: Option to open the console in your default web browser
- **Connection Testing**: Test connectivity to the switch with detailed status feedback
- **Configurable Switch URL**: Easily change the switch IP address through the GUI
- **System Tray Integration**: Minimize to system tray instead of closing (Linux)
- **Modern UI**: Clean, responsive interface with optimized layout
- **Multi-Monitor Support**: Automatically opens on your primary monitor
- **Linux Native**: Optimized for all Linux distributions

## Requirements

- **Python**: 3.7 or higher
- **Network Access**: Connection to your network switch
- **Operating System**: Linux (all major distributions)

### System Requirements

- WebKitGTK (for embedded webview)
- GTK+ 3.0 development libraries
- Python Tkinter support

## Installation

### Linux Installation

#### Automatic Installation (Recommended)

The easiest way to install all dependencies is using the universal installer script that supports all major Linux distributions:

```bash
./installers/install-dependencies.sh
```

This script will:
- Detect your Linux distribution automatically
- Install all required system packages
- Install Python dependencies via pip
- Handle all desktop environments

**Supported Linux Distributions:**
- Debian/Ubuntu/Mint/Pop!_OS/Elementary OS (apt)
- Fedora/RHEL/CentOS (dnf/yum)
- Arch/Manjaro/EndeavourOS/Garuda (pacman)
- openSUSE/SLE (zypper)
- Alpine Linux (apk)
- Solus (eopkg)
- Gentoo (emerge)
- NixOS (nix)
- GuixSD (guix)
- Void Linux (xbps)

**Supported Desktop Environments:**
- GNOME
- KDE Plasma
- XFCE
- Cinnamon
- MATE
- LXDE/LXQt
- Budgie
- Pantheon
- Deepin
- Generic GTK-based environments

#### Manual Installation (Linux)

If you prefer to install manually:

1. Install system dependencies (varies by distribution):
   - **Debian/Ubuntu**: 
     ```bash
     sudo apt install python3 python3-pip python3-tk python3-dev libwebkit2gtk-4.0-dev libgtk-3-dev
     ```
   - **Fedora**: 
     ```bash
     sudo dnf install python3 python3-pip python3-tkinter python3-devel webkit2gtk3-devel gtk3-devel
     ```
   - **Arch/Manjaro**: 
     ```bash
     sudo pacman -S python python-pip python-tkinter webkit2gtk
     ```

2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install pywebview requests Pillow pystray
   ```

#### Desktop Entry (Linux - Optional)

To add YaP Switch Manager to your application menu:

```bash
./installers/install-desktop-entry.sh
```

This will create a desktop entry so you can launch the application from your application menu or launcher.

## Usage

**Recommended**: Use the launcher script (automatically checks dependencies):
```bash
./launchers/start-switch-manager.sh
```

Or run directly:
```bash
python3 core/switch_manager.py
```

### Application Features

1. **Configure Switch URL**:
   - Enter the switch IP address in the "Switch URL" field
   - Click "Update" or press Enter to save
   - The URL is validated and normalized automatically

2. **Open Switch Console (Embedded)**:
   - Opens the switch web console in an embedded window
   - Runs in a separate process for stability
   - Automatically falls back to external browser if webview fails

3. **Open in External Browser**:
   - Opens the switch console in your default web browser
   - Useful if the embedded console has issues

4. **Test Connection**:
   - Tests connectivity to the switch
   - Shows detailed connection status in a popup dialog
   - Helps diagnose network issues

5. **System Tray (Linux)**:
   - Clicking the X button minimizes to system tray
   - Right-click tray icon to show window or quit
   - Keeps the application running in the background

## Configuration

### Changing the Switch URL

The switch URL can be changed directly in the application:

1. Enter the new IP address in the "Switch URL" field (e.g., `192.168.1.1` or `http://192.168.1.1`)
2. Click "Update" or press Enter
3. The URL is automatically validated and normalized

The application supports:
- IP addresses without protocol (automatically adds `http://`)
- Full URLs with `http://` or `https://`
- Automatic trailing slash normalization

### Default Configuration

By default, the switch URL is set to `http://192.168.2.1/`. This can be changed in the GUI or by editing `core/switch_manager.py`:

```python
self.switch_url = "http://192.168.2.1/"
```

## Troubleshooting

### Connection Failed

If you see a "Connection Failed" message:

1. Ensure the switch is powered on
2. Verify you're on the same network as the switch
3. Check if the switch IP address has changed
4. Try opening in an external browser to see if the console loads there
5. Use the "Test Connection" button to diagnose issues

### Webview Not Loading

If the embedded console doesn't load:

- The application will automatically fall back to opening in your default browser
- Make sure you have a modern web browser installed (required by pywebview)
- Ensure WebKitGTK is installed (the dependency installer handles this automatically on Linux)
### Missing Dependencies

1. Run the dependency installer: `./installers/install-dependencies.sh`
2. Or install manually: `pip install pywebview requests Pillow pystray`

The launcher scripts will automatically detect missing dependencies and offer to install them.

### Window Opens on Wrong Monitor

The application automatically detects your primary monitor and opens there. If it still opens on the wrong monitor:

- The application uses xrandr (Linux) to detect the primary monitor
- Falls back to positioning at (100, 100) which should be on the primary monitor
- Test connection popup uses the same detection logic

### System Tray Not Working (Linux)

If the system tray icon doesn't appear:

- Ensure `pystray` is installed: `pip install pystray`
- Some desktop environments may require additional packages
- Try restarting the application

## Project Structure

```
YaP-Switch-Manager/
├── core/
│   ├── switch_manager.py      # Main application
│   └── webview_launcher.py     # Webview subprocess launcher
├── installers/
│   ├── install-dependencies.sh # Dependency installer
│   └── install-desktop-entry.sh # Desktop entry installer
├── launchers/
│   └── start-switch-manager.sh  # Launcher script
├── build.sh                     # Build script for AppImage
├── requirements.txt            # Python dependencies
├── yap-switch-manager.desktop  # Linux desktop entry template
├── icon.png                    # Application icon
├── LICENSE                     # License file
└── README.md                   # This file
```

## Dependencies

### Python Packages

- **pywebview** (>=4.0.0): Embedded web browser for console display
- **requests** (>=2.28.0): HTTP library for connection testing
- **Pillow** (>=9.0.0): Image processing for icons
- **pystray** (>=0.19.0): System tray support (Linux)

### System Packages (Linux)

- Python 3.7+ with Tkinter
- WebKitGTK (for pywebview)
- GTK+ 3.0 development libraries
- Image processing libraries (for Pillow)

## Development

### Running from Source

1. Clone or download the repository
2. Install dependencies (see Installation section)
3. Run: `python3 core/switch_manager.py`

### Building Standalone Executables

#### Building AppImage

The build script creates an optimized AppImage for all Linux distributions:

```bash
./build.sh [VERSION]
```

**Example:**
```bash
./build.sh 1.0.0
```

**Output:**
- **AppImage**: `YaP-Switch-Manager-1.0.0.AppImage`
  - Works on all Linux distributions (Debian, Ubuntu, Fedora, Arch, Manjaro, openSUSE, etc.)
  - Works with all desktop environments (GNOME, KDE, XFCE, Cinnamon, MATE, etc.)
  - Includes all dependencies
  - Optimized for fast startup
  - No installation required - just make executable and run

**Requirements for building:**
- Python 3.7+
- PyInstaller (automatically installed if missing)
- appimagetool (automatically downloaded if not found)

## License

© YaP Labs

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or feature requests, please open an issue on the project repository.

---

**Note**: This application requires network access to your switch. Ensure your firewall allows connections to the switch's IP address.
