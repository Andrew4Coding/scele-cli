# PyInstaller spec — builds a single-file `scele` binary.
#   pyinstaller packaging/scele.spec --clean --noconfirm
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Ship the package's non-Python files (the TUI stylesheet at
# scele/tui/styles/app.tcss). The TUI is optional: if `textual` was not
# installed at build time it is simply absent and `scele tui` prints an
# install hint instead.
datas = collect_data_files("scele")
hiddenimports = collect_submodules("scele")

try:  # only when the [tui] extra was installed into the build environment
    datas += collect_data_files("textual")
    hiddenimports += collect_submodules("textual")
except Exception:
    pass

a = Analysis(
    ["entry.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "playwright"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="scele",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
