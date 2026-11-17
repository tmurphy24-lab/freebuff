@echo off
rem Freebuff post-save formatter hook
rem Runs prettier on edited files if prettier is available

set "FILE=%1"
if "%FILE%"=="" exit /b 0

rem Only format supported file extensions
echo %FILE% | findstr /i "\.ts$ \.js$ \.json$ \.md$" >nul
if %errorlevel% neq 0 exit /b 0

where npx >nul 2>nul
if %errorlevel% equ 0 (
    call npx prettier --write "%FILE%" >nul 2>nul
)

exit /b 0
