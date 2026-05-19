#!/bin/bash
echo ""
echo "========================================"
echo "  ScriptBreaker"
echo "  Instalando dependencias..."
echo "========================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado."
    echo "Por favor instala Python desde: https://www.python.org/downloads/"
    exit 1
fi

echo "Instalando librerías necesarias..."
pip3 install customtkinter pdfplumber openpyxl Pillow --quiet
echo ""
echo "Listo! Iniciando ScriptBreaker..."
echo ""
cd "$(dirname "$0")"
python3 main.py
