#!/usr/bin/env python3
"""
Webview launcher - runs in separate process to avoid threading issues
"""
import sys
import webview

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: webview_launcher.py <url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        window = webview.create_window(
            'YaP Switch Manager',
            url,
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

