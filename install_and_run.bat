@echo off
title ScriptBreaker Pro - Instalador
echo.
echo ========================================
echo   ScriptBreaker Pro
echo   Instalando dependencias...
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado.
    echo Por favor descarga Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo Instalando librerias necesarias...
pip install customtkinter pdfplumber openpyxl Pillow --quiet
echo.
echo Listo! Iniciando ScriptBreaker Pro...
echo.
cd /d "%~dp0"
python main.py
pause
