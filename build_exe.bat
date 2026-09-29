@echo off
rem Build a single-file GUI exe with PyInstaller.
setlocal
cd /d "%~dp0"
py build_exe.py %*
pause
