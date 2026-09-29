@echo off
rem Dev launcher: double-click to start the GUI.
rem A packaged build would be dist\OOPLab.exe instead.
setlocal
cd /d "%~dp0"
set "PYW=C:\Program Files\Python310\pythonw.exe"
if exist "%PYW%" (
  start "" "%PYW%" "%~dp0oop_app.py"
) else (
  start "" pyw "%~dp0oop_app.py"
)
exit /b 0
