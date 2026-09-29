@echo off
rem oop_lab unified build script (shared by all problems)
rem usage: build.bat [source.cpp]
setlocal
if "%~1"=="" (
  echo [build] usage: build.bat ^<source.cpp^>
  exit /b 2
)
set "SRC=%~f1"
for %%I in ("%SRC%") do (set "SRCDIR=%%~dpI" & set "NAME=%%~nI")
rem %%~dpI always ends with a backslash; strip it for consistent quoting
if "%SRCDIR:~-1%"=="\" set "SRCDIR=%SRCDIR:~0,-1%"
if not exist "%SRCDIR%\build" mkdir "%SRCDIR%\build"
"C:\Users\yat0\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin\g++.EXE" -std=c++17 -O0 -g -Wall -Wextra -o "%SRCDIR%\build\%NAME%.exe" "%SRC%"
exit /b %ERRORLEVEL%
