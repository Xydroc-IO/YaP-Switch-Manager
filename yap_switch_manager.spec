# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['core/switch_manager.py'],
    pathex=['/home/xydroc/Documents/GitHub/YaP-Switch-Manager'],
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
    icon='icon.png',
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
