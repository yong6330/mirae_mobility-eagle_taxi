# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['eagle_taxi_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('build_assets', 'dist/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EagleTaxiLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['build_assets/EagleTaxiLogo.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EagleTaxiLauncher',
)
app = BUNDLE(
    coll,
    name='EagleTaxiLauncher.app',
    icon='build_assets/EagleTaxiLogo.icns',
    bundle_identifier=None,
)
