# 🎬 ScriptBreaker

Herramienta de desglose automático de guiones cinematográficos y teatrales. Carga un PDF de guion y genera un Excel de producción con una pestaña por personaje, desglose por escenas, locaciones, EXT/INT, DÍA/NOC, vestuario (KBIO) y observaciones.

## 🌐 Acceso web

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://TU-APP.streamlit.app)

> Reemplaza el link de arriba con el URL real después del deploy.

## 💻 Instalación local

**Windows:**
Doble clic en install_and_run.bat

**Mac / Linux:**
Doble clic en install_and_run.command

**Manual:**
```bash
pip install -r requirements.txt
python main.py          # App de escritorio
streamlit run web_app.py  # App web (localhost:8501)
```

## 📊 Qué genera

- Una pestaña Excel por personaje principal con todas sus escenas
- Columnas: KBIO · CAP · ESC · LOCACION · EXT · INT · DIA · NOC · OBSERVACION · CONTINUIDAD
- Pestaña EXTRAS Y FIGURANTES
- Pestaña CAMBIOS de vestuario
- Observaciones automáticas: edad, vestuario, props, acciones físicas, personajes en escena

## 🛠 Stack

- Parser: Python puro + regex + pdfplumber (sin IA, sin APIs)
- Excel: openpyxl
- Web: Streamlit
- Desktop: CustomTkinter

## 📋 Formato de guion soportado

Guiones en formato Hollywood estándar con cabeceras tipo:
```
3   INT. APOLOS. TARIMA - CONTINUO
9   EXT. FACHADA APARTAMENTO - AMANECER
```
