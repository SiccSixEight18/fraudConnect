@echo off
REM build_exe.bat
setlocal enabledelayedexpansion

REM Find Python installation
for /f "tokens=*" %%i in ('where python') do (
    set PYTHON_PATH=%%i
    goto :found_python
)

REM Check Program Files for Python if not found in PATH
if exist "C:\Program Files\Python*" (
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH="%%i\python.exe"
            set PIP_PATH="%%i\Scripts\pip.exe"
            goto :found_python
        )
    )
)

if exist "C:\Program Files (x86)\Python*" (
    for /d %%i in ("C:\Program Files (x86)\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH="%%i\python.exe"
            set PIP_PATH="%%i\Scripts\pip.exe"
            goto :found_python
        )
    )
)

REM Check Users directory for Python
if exist "%LOCALAPPDATA%\Programs\Python*" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH="%%i\python.exe"
            set PIP_PATH="%%i\Scripts\pip.exe"
            goto :found_python
        )
    )
)

:python_not_found
echo Python installation not found!
echo Please install Python from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:found_python
echo Found Python at: %PYTHON_PATH%

REM Install required packages
echo Installing required packages...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install pyinstaller streamlit networkx matplotlib pandas

REM Check if PyInstaller is installed correctly
"%PYTHON_PATH%" -m pyinstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: PyInstaller installation failed
    pause
    exit /b 1
)

echo Creating executable...
"%PYTHON_PATH%" -m pyinstaller --onefile ^
    --add-data "app.py;." ^
    --hidden-import streamlit ^
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs ^
    --hidden-import streamlit.runtime.scriptrunner.script_runner ^
    --hidden-import streamlit.web.server.server ^
    --hidden-import streamlit.web.server.server_util ^
    --hidden-import streamlit.runtime.credentials ^
    --hidden-import streamlit.runtime.media_file_manager ^
    --name FraudViz ^
    fraud_viz.py

if %ERRORLEVEL% NEQ 0 (
    echo Error: Executable creation failed
    pause
    exit /b 1
)

echo.
echo Executable created successfully!
echo You can find FraudViz.exe in the dist folder
echo.
pause