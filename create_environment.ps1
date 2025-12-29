$ErrorActionPreference="Stop"

$env:PATH = "C:\dev\msys64\mingw64\bin;$env:PATH"

C:\dev\msys64\mingw64\bin\python.exe -m venv .venv

.\.venv\bin\Activate.ps1

python -c "import sys; print(sys.base_prefix)"

where python
python -c "import gi; print('gi OK')"
gst-launch-1.0 --version