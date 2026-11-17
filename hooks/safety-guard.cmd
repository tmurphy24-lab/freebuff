@echo off
set "CMD=%*"
if not defined CMD exit /b 0

echo %CMD% | findstr /i /c:"git push --force" /c:"git push -f" >nul
if %errorlevel% equ 0 (
    echo [BLOCKED BY SAFETY HOOK] Force pushing to git is prohibited.
    exit /b 1
)

echo %CMD% | findstr /i /c:"rm -rf" /c:"rmdir /s" /c:"format" >nul
if %errorlevel% equ 0 (
    echo [BLOCKED BY SAFETY HOOK] Destructive disk wiping command detected.
    exit /b 1
)

exit /b 0
