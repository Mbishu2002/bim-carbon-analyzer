# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = [('data/lca_database.csv', 'data'), ('data/samples', 'data/samples')]
binaries = []
hiddenimports = ['openpyxl', 'PySide6.QtSvg']
datas += collect_data_files('matplotlib')
tmp_ret = collect_all('ifcopenshell')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('qtawesome')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\User\\Desktop\\PythonProject_Fabrice\\PythonProject\\app.py'],
    pathex=['C:\\Users\\User\\Desktop\\PythonProject_Fabrice\\PythonProject'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='BIM_Carbon_Analyzer',
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
)
