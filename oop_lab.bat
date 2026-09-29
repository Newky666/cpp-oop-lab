@echo off
rem ============================================================
rem  C++ OOP Lab - just double click this file
rem  It opens an interactive menu: plan / learn / practice /
rem  judge / profile / find problems / self-check
rem  You can also pass arguments, e.g.  oop_lab.bat judge b01
rem ============================================================
chcp 65001 >nul
cd /d "%~dp0"

if "%~1"=="" (
    py oop_lab.py menu
    echo.
    pause
) else (
    py oop_lab.py %*
)
