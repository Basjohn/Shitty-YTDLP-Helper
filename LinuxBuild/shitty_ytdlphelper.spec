# -*- mode: python ; coding: utf-8 -*-

import platform

block_cipher = None

# Platform-specific settings
is_windows = platform.system() == 'Windows'
icon_ext = 'ico' if is_windows else 'png'


a = Analysis(
    ['shitty_ytdlphelper.py'],
    pathex=[],
    binaries=[],
    datas=[(f'SYHS.{icon_ext}', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='shitty_ytdlphelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=is_windows,  # Only use UPX on Windows by default
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[f'SYHS.{icon_ext}'] if is_windows else None,  # Only set icon for Windows
    # Linux-specific settings
    upx=True if is_windows else False,  # Disable UPX on Linux by default as it might cause issues
    upx_exclude=[],
)
