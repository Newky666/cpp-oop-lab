@echo off
rem oop_lab: run one test case
rem usage: run_case.bat [problem-dir] [case-no]
setlocal
set "DIR=%~f1"
set "N=%~2"
if "%DIR%"=="" (
  echo [run] usage: run_case.bat ^<problem-dir^> ^<case-no^>
  exit /b 2
)
if "%N%"=="" set "N=1"
set "PAD=0%N%"
if %N% GEQ 10 set "PAD=%N%"
set "IN=%DIR%\tests\%PAD%.in"
if not exist "%IN%" (
  echo [run] no such test case: %IN%
  exit /b 2
)
if not exist "%DIR%\build\main.exe" (
  call "%~dp0build.bat" "%DIR%\main.cpp"
  if errorlevel 1 exit /b 1
)
echo [run] input file: %IN%
"%DIR%\build\main.exe" < "%IN%"
exit /b %ERRORLEVEL%
