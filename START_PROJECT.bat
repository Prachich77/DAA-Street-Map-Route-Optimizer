@echo off
setlocal
cd /d "%~dp0"
if not exist "main.py" (
    echo ERROR: Place these launcher files in the project folder beside main.py.
    pause
    exit /b 1
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "launch_project.py"
) else (
    echo ERROR: Project virtual environment .venv was not found.
    echo Complete the environment setup in README first.
    pause
    exit /b 1
)
if errorlevel 1 pause
endlocal
