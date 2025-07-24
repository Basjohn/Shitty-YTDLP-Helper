# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['shitty_ytdlphelper.py'],
    pathex=[],
    binaries=[],
    datas=[('F:\\Programming\\Apps\\SYH\\rc\\SYHSB.ico', 'rc'), ('F:\\Programming\\Apps\\SYH\\rc\\SYHSB.png', 'rc'), ('F:\\Programming\\Apps\\SYH\\rc\\SYHSB.ico', 'rc')],
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
    name='ShittyYTDLPHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['F:\\Programming\\Apps\\SYH\\rc\\SYHSB.ico'],
)
