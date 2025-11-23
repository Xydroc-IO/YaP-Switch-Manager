<div align="center">

![YaP Switch Manager](icon.png)

# YaP Switch Manager

A modern, cross-platform desktop application to manage your network switch via its web console. Features a clean, intuitive interface with embedded webview support, system tray integration, and comprehensive multi-monitor support.

</div>

## Features

- **Multiple Switch Management**: Save and manage multiple switches with custom names
- **Embedded Console**: Open multiple switch web consoles in separate embedded windows simultaneously
- **Switch Persistence**: Save switch configurations (name + URL) for easy recall
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

1. **Save Switches**:
   - Enter a switch name and URL in the "Add/Edit Switch" section
   - Click "Save Switch" or press Enter to save the configuration
   - Saved switches are stored persistently and can be recalled later
   - Switch configurations are saved to `~/.config/yap-switch-manager/switches.json` (Linux/Mac) or `%APPDATA%\YaP-Switch-Manager\switches.json` (Windows)

2. **Load Saved Switches**:
   - All saved switches appear in the "Saved Switches" listbox
   - Click on a switch in the list to select it
   - Click "Load" to load the switch's configuration into the form fields
   - The switch name and URL will be populated automatically

3. **Delete Switches**:
   - Select a switch from the "Saved Switches" list
   - Click "Delete" to remove it from your saved switches
   - You'll be prompted to confirm before deletion

4. **Open Multiple Switch Consoles**:
   - You can open multiple switch console windows simultaneously
   - Each console window shows the switch name in its title bar
   - Configure different switches and click "Open Console (Embedded)" multiple times
   - Each switch console runs in its own separate process for stability

5. **Open Switch Console (Embedded)**:
   - Opens the currently configured switch's web console in an embedded window
   - Uses the name and URL from the form fields
   - Runs in a separate process for stability
   - Automatically falls back to external browser if webview fails

6. **Open in External Browser**:
   - Opens the currently configured switch console in your default web browser
   - Useful if the embedded console has issues
   - Uses the switch URL from the form fields

7. **Test Connection**:
   - Tests connectivity to the currently configured switch
   - Shows detailed connection status in a popup dialog
   - Helps diagnose network issues
   - Uses the switch URL from the form fields

8. **System Tray (Linux)**:
   - Clicking the X button minimizes to system tray
   - Right-click tray icon to show window or quit
   - Keeps the application running in the background

## Configuration

### Managing Switches

Switches are managed through the GUI interface:

1. **Adding a New Switch**:
   - Enter a name for the switch (e.g., "Main Switch", "Office Switch")
   - Enter the switch URL (e.g., `192.168.1.1` or `http://192.168.1.1`)
   - Click "Save Switch" or press Enter
   - The switch will appear in the "Saved Switches" list

2. **Loading a Saved Switch**:
   - Click on a switch in the "Saved Switches" list to select it
   - Click "Load" to populate the form fields with that switch's configuration
   - The switch name and URL will be loaded into the "Add/Edit Switch" section

3. **Editing a Switch**:
   - Load the switch you want to edit
   - Modify the name or URL in the form fields
   - Click "Save Switch" to update the configuration

4. **Deleting a Switch**:
   - Select the switch from the "Saved Switches" list
   - Click "Delete"
   - Confirm the deletion in the popup dialog

### Switch Storage

Switch configurations are stored persistently in a JSON file:
- **Linux/Mac**: `~/.config/yap-switch-manager/switches.json`
- **Windows**: `%APPDATA%\YaP-Switch-Manager\switches.json`

Each switch configuration contains:
- **name**: Display name for the switch
- **url**: Full URL to the switch's web console

The storage file is created automatically when you save your first switch. You can manually edit this file if needed, but the GUI is the recommended way to manage switches.

### URL Format

The application supports flexible URL formats:
- IP addresses without protocol (automatically adds `http://`)
- Full URLs with `http://` or `https://`
- Automatic trailing slash normalization

**Examples:**
- `192.168.1.1` → `http://192.168.1.1/`
- `192.168.1.1/` → `http://192.168.1.1/`
- `http://192.168.1.1` → `http://192.168.1.1/`
- `https://switch.example.com` → `https://switch.example.com/`

### Default Configuration

By default, when you first run the application, the URL field is pre-filled with `http://192.168.2.1/`. You can change this by:
- Entering a different URL in the form and saving it as a switch
- The default URL is just a starting point and can be modified at any time

## Advanced Usage

### Managing Multiple Switches

YaP Switch Manager supports managing multiple switches simultaneously:

1. **Save Multiple Switches**:
   - Add each switch configuration with a unique name
   - All saved switches appear in the "Saved Switches" list
   - Switch names help you identify which switch is which

2. **Open Multiple Consoles**:
   - Load a switch configuration from the saved list
   - Click "Open Console (Embedded)" to open its console
   - Load a different switch and click "Open Console (Embedded)" again
   - Each console opens in its own window with the switch name in the title
   - You can manage multiple switches at the same time

3. **Quick Switching**:
   - Use the "Saved Switches" list to quickly load different switch configurations
   - Click on a switch in the list to select it
   - Click "Load" to populate the form fields
   - Open its console without re-entering the URL

### Switch Storage Format

The switch storage file (`switches.json`) uses a simple JSON format:

```json
{
  "Main Switch": {
    "name": "Main Switch",
    "url": "http://192.168.1.1/"
  },
  "Office Switch": {
    "name": "Office Switch",
    "url": "http://192.168.2.1/"
  }
}
```

You can manually edit this file to add or modify switches, but the GUI is the recommended method.

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

### Saved Switches Not Appearing

If your saved switches don't appear in the list:

- Check if the storage file exists: `~/.config/yap-switch-manager/switches.json` (Linux/Mac)
- Ensure the file is valid JSON format
- Try saving a new switch to create the storage file
- Check file permissions on the config directory

### Multiple Console Windows

If you have issues with multiple console windows:

- Each console runs in a separate process for stability
- Console windows are independent and can be closed individually
- The switch name appears in each console window's title bar
- Closing a console window doesn't affect other open consoles

## Project Structure

```
YaP-Switch-Manager/
├── core/
│   ├── switch_manager.py      # Main application and GUI
│   ├── switch_storage.py      # Switch configuration storage system
│   └── webview_launcher.py    # Webview subprocess launcher
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

Note: All packages are automatically installed when using the dependency installer script.

### System Packages (Linux)

- Python 3.7+ with Tkinter
- WebKitGTK (for pywebview)
- GTK+ 3.0 development libraries
- Image processing libraries (for Pillow)

## Development

### Running from Source

1. Clone or download the repository
2. Install dependencies (see Installation section)
3. Run using the launcher script:
   ```bash
   ./launchers/start-switch-manager.sh
   ```
   Or run directly:
   ```bash
   python3 core/switch_manager.py
   ```

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


---

**Note**: This application requires network access to your switch. Ensure your firewall allows connections to the switch's IP address.
