# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Carpetas de recursos que la app abre con rutas relativas al directorio de
# trabajo (imagenes, iconos coloreados por tema, estilos JSON/QSS ya
# generados). Se copian junto al .exe para que esas rutas relativas sigan
# resolviendo igual que al ejecutar main.py desde el proyecto.
datas = [
    ('images', 'images'),
    ('json-styles', 'json-styles'),
    ('Qss', 'Qss'),
    ('generated-files', 'generated-files'),
]
binaries = []
hiddenimports = []

for pkg in ('automation1', 'Custom_Widgets'):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # El entorno tiene tambien PyQt5/PyQt6 instalados (usados por otras
    # herramientas), pero la app solo usa PySide6. Excluirlos evita que
    # PyInstaller aborte por detectar mas de un binding de Qt.
    excludes=['PyQt5', 'PyQt6', 'PySide2'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='laserMotionControl',
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
    # Desactiva la carpeta "_internal" (por defecto desde PyInstaller 6) para
    # que los recursos queden junto al .exe: el codigo abre "images/...",
    # "Qss/icons/..." y "json-styles/style.json" relativos al directorio de
    # trabajo, que al hacer doble clic es la carpeta del .exe.
    contents_directory='.',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='laserMotionControl',
)
