@echo off
title ScriptBreaker Pro — Web
echo.
echo ========================================
echo   ScriptBreaker Pro — Modo Web
echo ========================================
echo.
pip install streamlit --quiet
echo Iniciando servidor web...
echo.
echo Abre tu navegador en: http://localhost:8501
echo Para acceder desde celular/tablet usa:
echo   http://[IP-DE-TU-COMPUTADOR]:8501
echo.
echo Para encontrar tu IP: busca "ipconfig" (Windows)
echo.
cd /d "%~dp0"
streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
pause
