#!/usr/bin/env python3
"""
YaP Switch Manager
Desktop application to manage network switch via web console.
"""

import sys
import os
import webview
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
import subprocess

# Try to import Retry - handle different urllib3 versions
try:
    from urllib3.util.retry import Retry
except ImportError:
    try:
        from requests.packages.urllib3.util.retry import Retry
    except ImportError:
        # Fallback: define a simple retry strategy
        Retry = None

# Try to import PIL for icon support
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Try to import pystray for system tray support
try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

class SwitchManager:
    def __init__(self, initial_url="http://192.168.2.1/"):
        self.switch_url = initial_url
        self.window = None
        self.webview_process = None
        self.webview_running = False
        
        # Create optimized session for faster requests
        self.session = requests.Session()
        if Retry is not None:
            retry_strategy = Retry(
                total=1,
                backoff_factor=0.1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        
    def check_connection(self, callback=None):
        """Check if switch is reachable (async)."""
        def _check():
            try:
                # Use shorter timeout for faster response
                response = self.session.get(self.switch_url, timeout=1.5, stream=True)
                # Only read headers, not full body (faster)
                result = response.status_code == 200
                response.close()
            except:
                result = False
            
            if callback:
                callback(result)
            return result
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()
        return thread
    
    def open_console(self, skip_check=False, gui_callback=None):
        """Open switch console in embedded webview."""
        # Check if webview process is still running
        if self.webview_process is not None:
            # Check if process is still alive (poll() returns None if running)
            if self.webview_process.poll() is None:
                # Window already exists and is running
                return
            else:
                # Process has ended, reset state
                self.webview_running = False
                self.webview_process = None
        
        # Skip connection check for faster opening
        if skip_check:
            self._create_window_subprocess()
            return
        
        # Quick async connection check (non-blocking)
        def on_check_result(connected):
            if not connected:
                # Use callback to show dialog in GUI thread
                if gui_callback:
                    gui_callback(False)
                else:
                    # Fallback: just open anyway
                    self._create_window_subprocess()
            else:
                self._create_window_subprocess()
        
        # Start connection check (non-blocking)
        self.check_connection(on_check_result)
        # Also start window creation immediately (optimistic - faster UX)
        self._create_window_subprocess()
    
    def _create_window_subprocess(self):
        """Create webview window in a subprocess (required for pywebview)."""
        if self.webview_running:
            return
        
        try:
            self.webview_running = True
            # Get the directory where this script is located (core folder)
            # Handle both normal execution and PyInstaller bundled execution
            launcher_script = None
            
            if getattr(sys, 'frozen', False):
                # Running as bundled executable (PyInstaller/AppImage)
                # Try multiple locations for webview_launcher.py
                possible_paths = []
                
                # 1. In _MEIPASS/core (PyInstaller temp folder)
                if hasattr(sys, '_MEIPASS'):
                    possible_paths.append(os.path.join(sys._MEIPASS, 'core', 'webview_launcher.py'))
                
                # 2. Next to executable in core/ folder
                exe_dir = os.path.dirname(sys.executable)
                possible_paths.append(os.path.join(exe_dir, 'core', 'webview_launcher.py'))
                
                # 3. In usr/bin (AppImage structure)
                possible_paths.append(os.path.join(exe_dir, 'usr', 'bin', 'webview_launcher.py'))
                
                # 4. In same directory as executable
                possible_paths.append(os.path.join(exe_dir, 'webview_launcher.py'))
                
                # Try each path
                for path in possible_paths:
                    if os.path.exists(path):
                        launcher_script = path
                        break
            else:
                # Normal Python execution
                script_dir = os.path.dirname(os.path.abspath(__file__))
                launcher_script = os.path.join(script_dir, 'webview_launcher.py')
            
            # If still not found, try current working directory
            if not launcher_script or not os.path.exists(launcher_script):
                cwd_script = os.path.join(os.getcwd(), 'core', 'webview_launcher.py')
                if os.path.exists(cwd_script):
                    launcher_script = cwd_script
                else:
                    launcher_script = None
            
            # Determine which executable to use for running the launcher
            # For bundled executables, we need system Python, not the bundled app
            import shutil
            
            if getattr(sys, 'frozen', False):
                # We're bundled - find system Python
                python_exe = None
                for python_cmd in ['python3', 'python']:
                    if shutil.which(python_cmd):
                        python_exe = python_cmd
                        break
            else:
                # Not bundled - use sys.executable (which is Python)
                python_exe = sys.executable
            
            # Run webview in a subprocess
            if launcher_script and os.path.exists(launcher_script):
                if python_exe:
                    # Use launcher script with Python
                    try:
                        self.webview_process = subprocess.Popen(
                            [python_exe, launcher_script, self.switch_url],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=os.path.dirname(launcher_script) if launcher_script else None
                        )
                    except Exception as e:
                        print(f"Error launching webview with launcher: {e}")
                        python_exe = None  # Fall through to temp script
                else:
                    # No Python found - try to make launcher executable and run directly
                    try:
                        os.chmod(launcher_script, 0o755)
                        self.webview_process = subprocess.Popen(
                            [launcher_script, self.switch_url],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=os.path.dirname(launcher_script) if launcher_script else None
                        )
                    except Exception as e:
                        print(f"Error running launcher directly: {e}")
                        python_exe = None  # Fall through to temp script
            
            # Fallback: create temporary script (works for both bundled and non-bundled)
            if not (launcher_script and os.path.exists(launcher_script) and self.webview_process):
                import tempfile
                
                # Find Python for temp script
                if not python_exe:
                    for python_cmd in ['python3', 'python']:
                        if shutil.which(python_cmd):
                            python_exe = python_cmd
                            break
                
                if not python_exe:
                    raise RuntimeError("Python not found. Cannot launch webview.")
                
                # Create temp script that imports webview and runs it
                temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                temp_script.write(f'''#!/usr/bin/env python3
import sys
import webview
url = "{self.switch_url}"
try:
    window = webview.create_window('YaP Switch Manager', url, width=1200, height=800, min_size=(800, 600), resizable=True)
    webview.start(debug=False)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
''')
                temp_script.close()
                # Make executable
                os.chmod(temp_script.name, 0o755)
                
                try:
                    # Run with Python explicitly
                    self.webview_process = subprocess.Popen(
                        [python_exe, temp_script.name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except Exception as e:
                    print(f"Error launching webview fallback: {e}")
                    # Clean up temp file
                    try:
                        os.unlink(temp_script.name)
                    except:
                        pass
                    raise
            
            # Monitor process in background
            def monitor_process():
                try:
                    self.webview_process.wait()
                except Exception:
                    pass
                finally:
                    self.webview_running = False
                    self.webview_process = None
            
            threading.Thread(target=monitor_process, daemon=True).start()
        except Exception as e:
            import traceback
            error_msg = f"Error creating webview subprocess: {e}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.webview_running = False
            self.webview_process = None
            # Fallback to external browser
            try:
                webbrowser.open(self.switch_url)
            except Exception as browser_error:
                print(f"Error opening browser: {browser_error}", file=sys.stderr)
    
    def open_in_browser(self):
        """Open switch console in external browser."""
        webbrowser.open(self.switch_url)
    
    def test_connection(self, callback=None):
        """Test connection to switch (async)."""
        def _test():
            try:
                # Use optimized session with shorter timeout
                response = self.session.get(self.switch_url, timeout=1.5, stream=True)
                result = response.status_code == 200
                response.close()
            except Exception as e:
                print(f"Connection test error: {e}")  # Debug output
                result = False
            
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    print(f"Callback error: {e}")  # Debug output
            return result
        
        thread = threading.Thread(target=_test, daemon=True)
        thread.start()
        return thread
    
    def set_url(self, url):
        """Update the switch URL."""
        # Ensure URL ends with /
        if url and not url.endswith('/'):
            url += '/'
        # Ensure URL has protocol
        if url and not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.switch_url = url

class SwitchManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YaP Switch Manager")
        self.root.geometry("480x400")
        self.root.resizable(False, False)
        
        # System tray support
        self.tray_icon = None
        self.tray_thread = None
        self.hidden_to_tray = False
        
        # Configure modern styling
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # Switch manager instance
        self.manager = SwitchManager()
        
        # Setup UI first (faster)
        self.create_widgets()
        
        # Center the window on primary monitor (non-blocking, after widgets are created)
        def center_window():
            self.root.update_idletasks()
            # Get window dimensions
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # Try to get primary monitor dimensions using system commands
            primary_width = None
            primary_height = None
            
            try:
                # Try using xrandr to get primary monitor dimensions (Linux)
                import subprocess
                result = subprocess.run(['xrandr', '--query'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=1)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'primary' in line.lower() and 'connected' in line.lower():
                            # Parse resolution from line like: "HDMI-1 connected primary 1920x1080+0+0"
                            import re
                            match = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                            if match:
                                primary_width = int(match.group(1))
                                primary_height = int(match.group(2))
                                primary_x = int(match.group(3))
                                primary_y = int(match.group(4))
                                # Calculate center relative to primary monitor position
                                x = primary_x + (primary_width // 2) - (window_width // 2)
                                y = primary_y + (primary_height // 2) - (window_height // 2)
                                self.root.geometry(f"+{x}+{y}")
                                return
            except:
                pass
            
            # Fallback: Use root window position to determine primary monitor
            try:
                # Get root window position (should be on primary monitor)
                root_x = self.root.winfo_rootx()
                root_y = self.root.winfo_rooty()
                
                # If we can't detect primary, assume it's at (0,0) and use screen dimensions
                if primary_width is None:
                    # Get screen dimensions - try to use primary monitor size
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    
                    # On multi-monitor, screenwidth might be combined
                    # Try to get a reasonable primary monitor size (common sizes)
                    # Or use a conservative approach: position near top-left
                    if screen_width > 3840:  # Likely combined width
                        # Assume primary is one of the monitors, use a reasonable size
                        primary_width = min(3840, screen_width // 2)  # Assume 4K or half of combined
                        primary_height = min(2160, screen_height)
                    else:
                        primary_width = screen_width
                        primary_height = screen_height
                    
                    # Position at center of assumed primary monitor (starting from 0,0)
                    x = (primary_width // 2) - (window_width // 2)
                    y = (primary_height // 2) - (window_height // 2)
                    
                    # Ensure positive coordinates (primary monitor at 0,0)
                    x = max(50, min(x, primary_width - window_width - 50))
                    y = max(50, min(y, primary_height - window_height - 50))
                else:
                    # Use detected primary monitor
                    x = (primary_width // 2) - (window_width // 2)
                    y = (primary_height // 2) - (window_height // 2)
                    x = max(0, x)
                    y = max(0, y)
                
                self.root.geometry(f"+{x}+{y}")
            except:
                # Ultimate fallback: position at top-left area of primary monitor
                # Primary monitor always starts at (0,0), so this should work
                x = 100
                y = 100
                self.root.geometry(f"+{x}+{y}")
        
        # Also try to force window to appear on primary monitor by setting position before showing
        # This helps on some window managers
        self.root.geometry("+100+100")  # Temporary position to force primary monitor
        self.root.update_idletasks()
        
        # Set window icon (async, non-blocking)
        self.root.after_idle(self._set_window_icon)
        self.root.after_idle(center_window)
        
        # Setup system tray if available
        if HAS_PYSTRAY:
            self.setup_system_tray()
        
        # Handle window close - minimize to tray instead of closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _set_window_icon(self):
        """Set the window icon from icon file (non-blocking)."""
        def _load_icon():
            try:
                # Try to find icon.png in multiple locations (prioritize icon.png)
                # Handle both normal execution and PyInstaller bundled execution
                if getattr(sys, 'frozen', False):
                    # Running as bundled executable
                    if hasattr(sys, '_MEIPASS'):
                        base_paths = [sys._MEIPASS, os.path.dirname(sys.executable)]
                    else:
                        base_paths = [os.path.dirname(sys.executable)]
                else:
                    # Normal Python execution
                    base_paths = [
                        os.path.dirname(os.path.dirname(__file__)),
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        os.path.dirname(__file__)
                    ]
                
                icon_paths = []
                for base in base_paths:
                    icon_paths.extend([
                        os.path.join(base, "icon.png"),
                        os.path.join(base, "yaplab.png"),
                    ])
                
                icon_path = None
                for path in icon_paths:
                    if os.path.exists(path):
                        icon_path = path
                        break
                
                if icon_path and HAS_PIL:
                    try:
                        img = Image.open(icon_path)
                        self.icon_img = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, self.icon_img)
                    except:
                        pass
            except Exception:
                pass
        
        # Load icon in thread to avoid blocking
        threading.Thread(target=_load_icon, daemon=True).start()
    
    def create_widgets(self):
        """Create GUI widgets."""
        # Main container with modern padding (optimized for fit)
        main_frame = ttk.Frame(self.root, padding="16")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with icon - centered and modern (optimized spacing)
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 14))
        
        # Try to load and display icon
        icon_label = None
        if HAS_PIL:
            try:
                # Try to find icon.png in multiple locations (prioritize icon.png)
                # Handle both normal execution and PyInstaller bundled execution
                if getattr(sys, 'frozen', False):
                    # Running as bundled executable
                    if hasattr(sys, '_MEIPASS'):
                        base_paths = [sys._MEIPASS, os.path.dirname(sys.executable)]
                    else:
                        base_paths = [os.path.dirname(sys.executable)]
                else:
                    # Normal Python execution
                    base_paths = [
                        os.path.dirname(os.path.dirname(__file__)),
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        os.path.dirname(__file__)
                    ]
                
                icon_paths = []
                for base in base_paths:
                    icon_paths.extend([
                        os.path.join(base, "icon.png"),
                        os.path.join(base, "yaplab.png"),
                    ])
                
                icon_path = None
                for path in icon_paths:
                    if os.path.exists(path):
                        icon_path = path
                        break
                
                if icon_path:
                    img = Image.open(icon_path)
                    # Resize icon to a reasonable size (56x56 for better fit)
                    img.thumbnail((56, 56), Image.Resampling.LANCZOS)
                    self.title_icon_img = ImageTk.PhotoImage(img)
                    icon_label = ttk.Label(title_frame, image=self.title_icon_img)
                    icon_label.pack(pady=(0, 8))
            except Exception:
                # Icon loading failed, continue without icon
                pass
        
        title_label = ttk.Label(
            title_frame,
            text="YaP Switch Manager",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Network Switch Web Console",
            font=("Segoe UI", 9),
            foreground="#666666"
        )
        subtitle_label.pack(pady=(4, 0))
        
        # Switch info frame - modern styling (optimized padding)
        info_frame = ttk.LabelFrame(main_frame, text="Switch Configuration", padding="12")
        info_frame.pack(fill=tk.X, pady=(0, 12))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Switch URL:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # URL entry field with modern styling
        url_frame = ttk.Frame(info_frame)
        url_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(8, 0), pady=5)
        url_frame.columnconfigure(0, weight=1)
        
        self.url_var = tk.StringVar(value=self.manager.switch_url)
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Consolas", 9), width=20)
        url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        # Allow Enter key to update URL
        url_entry.bind('<Return>', lambda e: self.update_url())
        
        # Save URL button - modern styling
        save_url_btn = ttk.Button(url_frame, text="Update", command=self.update_url, width=9)
        save_url_btn.grid(row=0, column=1, sticky=tk.W)
        
        # URL status label
        self.url_status_label = ttk.Label(info_frame, text="", font=("Segoe UI", 8))
        self.url_status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(3, 0))
        
        # Buttons frame - modern grid layout (optimized spacing)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # Open in embedded window button - primary action
        open_embedded_btn = ttk.Button(
            buttons_frame,
            text="Open Console (Embedded)",
            command=self.open_embedded
        )
        open_embedded_btn.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=2, pady=4)
        
        # Open in browser button
        open_browser_btn = ttk.Button(
            buttons_frame,
            text="Open in Browser",
            command=self.open_browser
        )
        open_browser_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(2, 4), pady=4)
        
        # Test connection button - secondary action
        test_btn = ttk.Button(
            buttons_frame,
            text="Test Connection",
            command=self.test_connection
        )
        test_btn.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(4, 2), pady=4)
        
        # Footer - modern styling (optimized padding)
        footer_label = ttk.Label(
            main_frame,
            text="© YaP Labs",
            font=("Segoe UI", 8),
            foreground="#999999"
        )
        footer_label.pack(side=tk.BOTTOM, pady=(4, 0))
    
    def open_embedded(self):
        """Open switch console in embedded window."""
        self.root.after_idle(lambda: self._open_embedded_async())
    
    def _open_embedded_async(self):
        """Open console asynchronously."""
        def on_connection_check(connected):
            """Handle connection check result in GUI thread."""
            if not connected:
                result = messagebox.askyesno(
                    "Connection Warning",
                    f"Could not reach switch at {self.manager.switch_url}\n\n"
                    "This might be normal if:\n"
                    "- The switch is not on the same network\n"
                    "- The IP address has changed\n"
                    "- The switch is not powered on\n\n"
                    "Would you like to open it anyway?",
                    icon='warning'
                )
                if not result:
                    return
            
            # Window is already opening (optimistic)
        
        try:
            # Open immediately (optimistic) - connection check happens in background
            self.manager.open_console(skip_check=False, gui_callback=on_connection_check)
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, lambda: self._show_error(error_details))
    
    def _show_error(self, error_msg):
        """Show error message."""
        messagebox.showerror("Error", f"Failed to open console: {error_msg}")
    
    def open_browser(self):
        """Open switch console in external browser."""
        # Open browser (non-blocking)
        self.root.after_idle(lambda: self._open_browser_async())
    
    def _open_browser_async(self):
        """Open browser asynchronously."""
        try:
            self.manager.open_in_browser()
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
    
    def update_url(self):
        """Update the switch URL from the entry field."""
        new_url = self.url_var.get().strip()
        
        if not new_url:
            self.url_status_label.config(text="❌ URL cannot be empty", foreground="#CC0000")
            return
        
        # Validate URL format
        try:
            from urllib.parse import urlparse
            # Add protocol if missing
            if not new_url.startswith(('http://', 'https://')):
                new_url = 'http://' + new_url
            
            # Validate URL
            parsed = urlparse(new_url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
            
            # Update manager URL
            self.manager.set_url(new_url)
            
            # Update entry field to show normalized URL
            self.url_var.set(self.manager.switch_url)
            
            # Show success message
            self.url_status_label.config(text=f"✅ URL updated to {self.manager.switch_url}", foreground="#00AA00")
            
            # Clear message after 3 seconds
            self.root.after(3000, lambda: self.url_status_label.config(text=""))
            
        except Exception as e:
            self.url_status_label.config(text=f"❌ Invalid URL: {str(e)}", foreground="#CC0000")
    
    def test_connection(self):
        """Test connection to switch - shows popup dialog."""
        # Update manager URL from entry field first
        current_url = self.url_var.get().strip()
        if current_url:
            try:
                if not current_url.startswith(('http://', 'https://')):
                    current_url = 'http://' + current_url
                self.manager.set_url(current_url)
            except:
                pass
        
        # Create status window
        status_window = tk.Toplevel(self.root)
        status_window.title("Connection Test")
        status_window.geometry("450x250")
        status_window.resizable(False, False)
        
        # Center the window on primary monitor (same logic as main window)
        def center_window():
            status_window.update_idletasks()
            window_width = status_window.winfo_width()
            window_height = status_window.winfo_height()
            
            # Try to get primary monitor dimensions using system commands
            primary_width = None
            primary_height = None
            
            try:
                # Try using xrandr to get primary monitor dimensions (Linux)
                import subprocess
                result = subprocess.run(['xrandr', '--query'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=1)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'primary' in line.lower() and 'connected' in line.lower():
                            # Parse resolution from line like: "HDMI-1 connected primary 1920x1080+0+0"
                            import re
                            match = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                            if match:
                                primary_width = int(match.group(1))
                                primary_height = int(match.group(2))
                                primary_x = int(match.group(3))
                                primary_y = int(match.group(4))
                                # Calculate center relative to primary monitor position
                                x = primary_x + (primary_width // 2) - (window_width // 2)
                                y = primary_y + (primary_height // 2) - (window_height // 2)
                                status_window.geometry(f"+{x}+{y}")
                                return
            except:
                pass
            
            # Fallback: Use root window position to determine primary monitor
            try:
                screen_width = status_window.winfo_screenwidth()
                screen_height = status_window.winfo_screenheight()
                
                if screen_width > 3840:  # Likely combined width
                    primary_width = min(3840, screen_width // 2)
                    primary_height = min(2160, screen_height)
                else:
                    primary_width = screen_width
                    primary_height = screen_height
                
                x = (primary_width // 2) - (window_width // 2)
                y = (primary_height // 2) - (window_height // 2)
                
                x = max(50, min(x, primary_width - window_width - 50))
                y = max(50, min(y, primary_height - window_height - 50))
                
                status_window.geometry(f"+{x}+{y}")
            except:
                # Ultimate fallback: position at top-left area of primary monitor
                status_window.geometry("+100+100")
        
        status_window.after_idle(center_window)
        
        frame = ttk.Frame(status_window, padding="25")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Testing Connection", font=("Segoe UI", 12, "bold")).pack(pady=(0, 15))
        
        status_label = ttk.Label(
            frame, 
            text="Connecting to switch...", 
            font=("Segoe UI", 10), 
            foreground="#0066CC",
            wraplength=400,
            justify=tk.LEFT
        )
        status_label.pack(pady=10, fill=tk.X)
        
        close_button = ttk.Button(frame, text="Close", command=status_window.destroy, state="disabled", width=15)
        close_button.pack(pady=(15, 0))
        
        def on_test_result(connected):
            """Update UI with test result."""
            if connected:
                status_label.config(
                    text=f"✓ Successfully connected to\n{self.manager.switch_url}",
                    foreground="#00AA00"
                )
            else:
                status_label.config(
                    text=f"✗ Failed to connect to {self.manager.switch_url}\n\n"
                         "Possible reasons:\n"
                         "• Switch is not on the same network\n"
                         "• IP address has changed\n"
                         "• Switch is not powered on",
                    foreground="#CC0000"
                )
            close_button.config(state="normal")
        
        # Start async connection test
        self.manager.test_connection(on_test_result)
    
    def setup_system_tray(self):
        """Setup system tray icon and menu."""
        if not HAS_PYSTRAY:
            return
        
        try:
            # Try to load icon for tray
            # Handle both normal execution and PyInstaller bundled execution
            if getattr(sys, 'frozen', False):
                # Running as bundled executable
                if hasattr(sys, '_MEIPASS'):
                    base_paths = [sys._MEIPASS, os.path.dirname(sys.executable)]
                else:
                    base_paths = [os.path.dirname(sys.executable)]
            else:
                # Normal Python execution
                base_paths = [
                    os.path.dirname(os.path.dirname(__file__)),
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    os.path.dirname(__file__)
                ]
            
            icon_paths = []
            for base in base_paths:
                icon_paths.extend([
                    os.path.join(base, "icon.png"),
                    os.path.join(base, "yaplab.png"),
                ])
            
            tray_image = None
            for path in icon_paths:
                if os.path.exists(path):
                    try:
                        tray_image = Image.open(path)
                        tray_image = tray_image.resize((64, 64), Image.Resampling.LANCZOS)
                        break
                    except:
                        pass
            
            # Fallback to a simple icon if image loading fails
            if not tray_image:
                tray_image = Image.new('RGB', (64, 64), color='#0066CC')
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem('Show Window', self.show_window),
                pystray.MenuItem('Quit', self.quit_application)
            )
            
            # Create tray icon
            self.tray_icon = pystray.Icon("YaP Switch Manager", tray_image, 
                                         "YaP Switch Manager", menu)
            
            # Start tray in separate thread
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"Warning: Could not setup system tray: {e}")
            self.tray_icon = None
    
    def show_window(self, icon=None, item=None):
        """Show the main window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.hidden_to_tray = False
    
    def hide_to_tray(self):
        """Hide window to system tray."""
        if self.tray_icon:
            self.root.withdraw()
            self.hidden_to_tray = True
    
    def quit_application(self, icon=None, item=None):
        """Quit the application."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def on_closing(self):
        """Handle window close event - minimize to tray instead of closing."""
        if HAS_PYSTRAY and self.tray_icon:
            # Minimize to tray instead of closing
            self.hide_to_tray()
        else:
            # No tray support, just close
            self.root.destroy()

def main():
    """Main entry point."""
    root = tk.Tk()
    app = SwitchManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

