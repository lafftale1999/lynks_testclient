# setup-gst-env.ps1
# Run in PowerShell:
#   PS> .\setup-gst-env.ps1
# If blocked by execution policy:
#   PS> powershell -ExecutionPolicy Bypass -File .\setup-gst-env.ps1

$ErrorActionPreference = "Stop"

# ---- Config ----
$MSYS2_ROOT = "C:\dev\msys64"
$MINGW_ROOT = Join-Path $MSYS2_ROOT "mingw64"
$MINGW_BIN  = Join-Path $MINGW_ROOT "bin"
$BASH_EXE   = Join-Path $MSYS2_ROOT "usr\bin\bash.exe"
$PY_EXE     = Join-Path $MINGW_BIN  "python.exe"
$VENV_DIR   = ".venv"
$ACTIVATE_  = "bin\activate.ps1"

# MSYS2 packages (64-bit MinGW)
$PKGS = @(
  "mingw-w64-x86_64-gstreamer",
  "mingw-w64-x86_64-gst-devtools",
  "mingw-w64-x86_64-gst-plugins-base",
  "mingw-w64-x86_64-gst-plugins-good",
  "mingw-w64-x86_64-gst-plugins-bad",
  "mingw-w64-x86_64-gst-plugins-ugly",
  "mingw-w64-x86_64-python",
  "mingw-w64-x86_64-python-gobject",
  "mingw-w64-x86_64-gobject-introspection-runtime",
  "mingw-w64-x86_64-gst-plugins-rs"
)

Write-Host "== Checking MSYS2 install paths =="
if (-not (Test-Path $BASH_EXE)) {
  throw "Missing: $BASH_EXE (check MSYS2_ROOT = $MSYS2_ROOT)"
}

# Ensure Python is installed via pacman if missing
if (-not (Test-Path $PY_EXE)) {
  Write-Host "== Python not found, installing via pacman =="
  & $BASH_EXE -lc "pacman -Sy --noconfirm mingw-w64-x86_64-python" | Write-Host
}

if (-not (Test-Path $PY_EXE)) {
  throw "Python still missing after install attempt: $PY_EXE"
}

# Make sure MinGW64 binaries/dlls come first for this PowerShell session
$env:PATH = "$MINGW_BIN;$env:PATH"

Write-Host "== Updating pacman databases / upgrading MSYS2 (safe to run multiple times) =="
# -lc runs a login shell so pacman sees the correct MSYS2 environment
& $BASH_EXE -lc "pacman -Sy --noconfirm" | Write-Host
& $BASH_EXE -lc "pacman -Syu --noconfirm" | Write-Host

Write-Host "== Installing required packages (if missing) =="
$pkgList = ($PKGS -join " ")
& $BASH_EXE -lc "pacman -S --needed --noconfirm $pkgList" | Write-Host

Write-Host "== (Re)creating venv from MSYS2 MinGW Python =="
if (Test-Path $VENV_DIR) {
  Write-Host "Removing existing $VENV_DIR"
  Remove-Item -Recurse -Force $VENV_DIR
}

# IMPORTANT: gi (PyGObject) comes from MSYS2's global Python, so we must inherit system site-packages
& $PY_EXE -m venv --system-site-packages $VENV_DIR

Write-Host "== Activating venv (PowerShell) =="
& (Join-Path $VENV_DIR $ACTIVATE_)

Write-Host "== Ensuring pip is available and up to date =="
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

if (Test-Path "requirements.txt") {
  Write-Host "== Installing Python dependencies from requirements.txt =="
  pip install -r requirements.txt
} else {
  Write-Host "== No requirements.txt found, skipping pip install =="
}

Write-Host "== Exporting runtime env vars for GI + GStreamer =="
# GI typelibs (Gst, GLib, etc.)
$env:GI_TYPELIB_PATH = (Join-Path $MINGW_ROOT "lib\girepository-1.0")

# GStreamer plugins
$gstPluginDir = Join-Path $MINGW_ROOT "lib\gstreamer-1.0"
$env:GST_PLUGIN_PATH = $gstPluginDir
$env:GST_PLUGIN_SYSTEM_PATH_1_0 = $gstPluginDir

# Optional but useful for debugging
# $env:GST_DEBUG = "2"

Write-Host "== Diagnostics =="
Write-Host ("python: " + (Get-Command python).Source)
python -c "import sys; print('base_prefix=', sys.base_prefix); print('prefix=', sys.prefix)"
Write-Host ("gst-launch-1.0: " + (Get-Command gst-launch-1.0).Source)
gst-launch-1.0 --version

Write-Host "== Verifying PyGObject (gi) + Gst bindings =="
python -c "import gi; print('gi OK:', gi.__file__)"
python -c "import gi; gi.require_version('Gst','1.0'); from gi.repository import Gst; Gst.init(None); print('Gst OK:', Gst.version_string())"

Write-Host ""
Write-Host "Done."
Write-Host "Next time, activate with:"
Write-Host "  .\.venv\" $ACTIVATE_
Write-Host ""
Write-Host "To exit the venv in PowerShell, run:"
Write-Host "  deactivate"
