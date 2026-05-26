@echo off
REM =====================================================================
REM  Build "Roku Remote" into a standalone Windows app (roku_remote.exe)
REM  -------------------------------------------------------------------
REM  Run this ONCE. After it finishes you never need Python again.
REM  Requirement: Python installed from python.org with
REM               "Add Python to PATH" checked during install.
REM
REM  Keep build_exe.bat, roku_remote.py, roku_remote/ folder and
REM  roku_remote.ico together in the SAME folder, then just
REM  double-click this file.
REM =====================================================================
setlocal
cd /d "%~dp0"

echo.
echo  [1/2] Installing the build tool (PyInstaller)...
echo.
python -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo.
echo  [2/2] Building roku_remote.exe ...
echo.
python -m PyInstaller --onefile --windowed --name roku_remote ^
    --icon roku_remote.ico ^
    --add-data "roku_remote.ico;." ^
    roku_remote.py
if errorlevel 1 goto :error

echo.
echo  =================================================================
echo   Done! Your standalone app is here:
echo.
echo      %~dp0dist\roku_remote.exe
echo.
echo   Double-click it to run. To put it on your desktop, right-click
echo   the exe and choose  Send to  ^>  Desktop (create shortcut).
echo   The icon is already baked into the file.
echo  =================================================================
echo.
pause
exit /b 0

:error
echo.
echo  ----------------------------------------------------------------
echo   Something went wrong.
echo   Check that Python is installed by opening Command Prompt and
echo   running:   python --version
echo   If that fails, reinstall Python and tick "Add Python to PATH",
echo   then run this file again.
echo  ----------------------------------------------------------------
echo.
pause
exit /b 1
