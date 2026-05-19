#!/bin/bash
echo ""
echo "========================================"
echo "  ScriptBreaker Pro — Modo Web"
echo "========================================"
echo ""
pip3 install streamlit --quiet
echo "Iniciando servidor web..."
echo ""
echo "Abre tu navegador en: http://localhost:8501"
echo "Para acceder desde celular/tablet usa:"
echo "  http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):8501"
echo ""
cd "$(dirname "$0")"
streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
