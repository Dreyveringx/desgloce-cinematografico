import streamlit as st
import sys
import os
import tempfile
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(
    page_title="ScriptBreaker",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "ScriptBreaker — Desglose automático de guiones cinematográficos"
    }
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

[data-testid="stSidebar"] {
    background-color: #1B3A4B !important;
    border-right: 1px solid #C9A84C40;
}
[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #C9A84C !important;
}

.app-header {
    background: linear-gradient(135deg, #1B3A4B 0%, #0d1117 60%);
    border: 1px solid #C9A84C40;
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.app-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    color: #C9A84C;
    margin: 0;
    letter-spacing: -0.5px;
}
.app-header p {
    color: #8b949e;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
}

.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #C9A84C;
    margin-bottom: 16px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C9A84C, #a8872d) !important;
    color: #0d1117 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 28px !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px #C9A84C50 !important;
}

.stButton > button[kind="secondary"] {
    background: #161b22 !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C60 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

[data-testid="stFileUploader"] {
    background-color: #161b22 !important;
    border: 2px dashed #4A6FA5 !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #C9A84C !important;
}
[data-testid="stFileUploadDropzone"] {
    background-color: transparent !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #4A6FA5, #C9A84C) !important;
    border-radius: 4px !important;
}

[data-testid="stCheckbox"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 3px 0;
    transition: border-color 0.2s;
}
[data-testid="stCheckbox"]:hover {
    border-color: #C9A84C60;
}

[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
[data-testid="stMetricValue"] {
    color: #C9A84C !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 8px;
    overflow: hidden;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #161b22;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #30363d;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8b949e !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background-color: #1B3A4B !important;
    color: #C9A84C !important;
}

[data-testid="stSuccess"] {
    background-color: #162417 !important;
    border-color: #2ea043 !important;
    color: #3fb950 !important;
    border-radius: 8px !important;
}
[data-testid="stError"] {
    background-color: #2d1519 !important;
    border-radius: 8px !important;
}
[data-testid="stInfo"] {
    background-color: #161b22 !important;
    border-color: #4A6FA5 !important;
    border-radius: 8px !important;
}

hr {
    border-color: #30363d !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4A6FA5; }

code {
    background-color: #161b22 !important;
    color: #C9A84C !important;
    border: 1px solid #30363d !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    padding: 2px 6px !important;
}

.char-badge {
    display: inline-block;
    background: #1B3A4B;
    border: 1px solid #4A6FA5;
    color: #C9A84C;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 2px;
}

.step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #30363d;
}
.step-num {
    width: 28px; height: 28px;
    background: #1B3A4B;
    border: 2px solid #4A6FA5;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: #C9A84C;
    flex-shrink: 0;
}
.step-num.done {
    background: #162417;
    border-color: #2ea043;
    color: #3fb950;
}
.step-text { font-size: 0.88rem; color: #8b949e; }
.step-text.done { color: #3fb950; }
</style>
""", unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="app-header">
        <div style="font-size:3rem;line-height:1">🎬</div>
        <div>
            <h1>ScriptBreaker</h1>
            <p>Desglose automático de guiones cinematográficos y teatrales</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_instructions(step: int):
    with st.sidebar:
        st.markdown("### Guía de uso")
        st.markdown("---")
        steps = [
            ("Carga tu PDF", "Sube el guion en formato cinematográfico estándar"),
            ("Analiza", "El sistema detecta escenas, personajes y locaciones"),
            ("Revisa", "Selecciona los personajes que quieres incluir"),
            ("Exporta", "Descarga el Excel de desglose de producción"),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            done = i < step
            cls = "done" if done else ""
            icon = "✓" if done else str(i)
            st.markdown(f"""
            <div class="step-row">
                <div class="step-num {cls}">{icon}</div>
                <div>
                    <div class="step-text {cls}" style="font-weight:600;color:{'#3fb950' if done else '#e6edf3'}">{title}</div>
                    <div class="step-text" style="font-size:0.78rem">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


if 'step' not in st.session_state:
    st.session_state.step = 1
if 'escenas' not in st.session_state:
    st.session_state.escenas = None
if 'personajes_p' not in st.session_state:
    st.session_state.personajes_p = []
if 'personajes_e' not in st.session_state:
    st.session_state.personajes_e = []
if 'breakdown' not in st.session_state:
    st.session_state.breakdown = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""


render_header()
render_sidebar_instructions(st.session_state.step)

if st.session_state.step == 1:
    col_upload, col_info = st.columns([3, 2], gap="large")

    with col_upload:
        st.markdown('<div class="card-title">📄 Cargar guion</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Arrastra tu PDF aquí o haz clic para seleccionar",
            type=["pdf"],
            label_visibility="collapsed"
        )

        if uploaded:
            size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            if size_mb > 50:
                st.error(f"El PDF pesa {size_mb:.1f} MB. El límite es 50 MB.")
                st.stop()

            st.session_state.pdf_bytes = uploaded.read()
            st.session_state.pdf_name = uploaded.name.replace('.pdf', '')

            st.markdown(f"""
            <div style="background:#162417;border:1px solid #2ea04360;border-radius:8px;
                        padding:14px 18px;margin-top:12px;display:flex;align-items:center;gap:12px">
                <span style="font-size:1.4rem">✅</span>
                <div>
                    <div style="color:#3fb950;font-weight:600;font-size:0.9rem">{uploaded.name}</div>
                    <div style="color:#8b949e;font-size:0.78rem">{len(st.session_state.pdf_bytes)/1024:.1f} KB · Listo para analizar</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍  Analizar guion", type="primary", key="btn_analyze"):
                st.session_state.step = 2
                st.rerun()

    with col_info:
        st.markdown('<div class="card-title">ℹ️ Qué genera esta app</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;flex-direction:column;gap:10px">
            <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px">
                <div style="color:#C9A84C;font-weight:600;margin-bottom:4px">📊 Excel de desglose</div>
                <div style="color:#8b949e;font-size:0.83rem">Una pestaña por personaje con escenas, locaciones, EXT/INT, DÍA/NOC, observaciones y KBIO</div>
            </div>
            <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px">
                <div style="color:#C9A84C;font-weight:600;margin-bottom:4px">👥 Extras y figurantes</div>
                <div style="color:#8b949e;font-size:0.83rem">Pestaña dedicada con agrupación por día de rodaje</div>
            </div>
            <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px">
                <div style="color:#C9A84C;font-weight:600;margin-bottom:4px">👗 Cambios de vestuario</div>
                <div style="color:#8b949e;font-size:0.83rem">Resumen de KBIO por personaje en la pestaña CAMBIOS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.step == 2:
    st.markdown('<div class="card-title">⚙️ Analizando guion...</div>', unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_text = st.empty()
    detail_text = st.empty()

    try:
        from app.core import breakdown_builder, pdf_reader, script_parser

        tmp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        tmp_file.write(st.session_state.pdf_bytes)
        tmp_file.flush()
        tmp_file.close()
        tmp_path = tmp_file.name

        status_text.markdown('<div style="color:#C9A84C;font-weight:500">Extrayendo texto del PDF...</div>', unsafe_allow_html=True)
        progress_bar.progress(10)
        time.sleep(0.3)

        try:
            text = pdf_reader.extract_text(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        detail_text.markdown(f'<div style="color:#8b949e;font-size:0.82rem">{len(text):,} caracteres extraídos</div>', unsafe_allow_html=True)

        status_text.markdown('<div style="color:#C9A84C;font-weight:500">Detectando escenas...</div>', unsafe_allow_html=True)
        progress_bar.progress(30)
        time.sleep(0.2)
        escenas = script_parser.parse_scenes(text)
        detail_text.markdown(f'<div style="color:#8b949e;font-size:0.82rem">{len(escenas)} escenas encontradas</div>', unsafe_allow_html=True)

        status_text.markdown('<div style="color:#C9A84C;font-weight:500">Identificando personajes...</div>', unsafe_allow_html=True)
        progress_bar.progress(55)
        time.sleep(0.2)
        p_p, p_e = script_parser.detect_characters(text, escenas)
        detail_text.markdown(f'<div style="color:#8b949e;font-size:0.82rem">{len(p_p)} personajes principales · {len(p_e)} extras</div>', unsafe_allow_html=True)

        status_text.markdown('<div style="color:#C9A84C;font-weight:500">Asignando días de rodaje...</div>', unsafe_allow_html=True)
        progress_bar.progress(70)
        escenas = script_parser.assign_shooting_days(escenas)
        script_parser.calculate_kbio(escenas, p_p)

        status_text.markdown('<div style="color:#C9A84C;font-weight:500">Construyendo desglose...</div>', unsafe_allow_html=True)
        progress_bar.progress(88)
        time.sleep(0.2)
        breakdown = breakdown_builder.build(escenas, p_p, p_e)

        progress_bar.progress(100)
        status_text.markdown('<div style="color:#3fb950;font-weight:600">✓ Análisis completado</div>', unsafe_allow_html=True)
        detail_text.empty()
        time.sleep(0.5)

        st.session_state.escenas = escenas
        st.session_state.personajes_p = p_p
        st.session_state.personajes_e = p_e
        st.session_state.breakdown = breakdown

        st.session_state.step = 3
        st.rerun()

    except Exception as e:
        import traceback
        st.error(f"Error durante el análisis: {e}")
        st.code(traceback.format_exc(), language="python")
        if st.button("← Volver e intentar con otro PDF"):
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 3:
    escenas = st.session_state.escenas
    p_p = st.session_state.personajes_p
    p_e = st.session_state.personajes_e
    breakdown = st.session_state.breakdown

    n_dias = len(set(e.dia_rodaje for e in escenas))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Escenas", len(escenas))
    col2.metric("Personajes", len(p_p))
    col3.metric("Extras", len(p_e))
    col4.metric("Días de rodaje", n_dias)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥  Personajes", "🎬  Escenas", "📋  Vista previa desglose"])

    with tab1:
        st.markdown('<div class="card-title">Selecciona los personajes a incluir en el Excel</div>', unsafe_allow_html=True)

        col_p, col_e = st.columns([1, 1], gap="large")

        with col_p:
            st.markdown("**Personajes principales**")
            char_selected = {}
            for char in p_p:
                n_esc = sum(1 for e in escenas if char in e.personajes)
                dias_char = len(set(e.dia_rodaje for e in escenas if char in e.personajes))
                label = f"{char}  —  {n_esc} esc · {dias_char} días"
                char_selected[char] = st.checkbox(label, value=True, key=f"chk_{char}")

        with col_e:
            st.markdown("**Extras y figurantes detectados**")
            for extra in p_e[:25]:
                n_esc = sum(1 for e in escenas if extra in e.extras)
                st.markdown(f"""
                <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;
                            padding:7px 14px;margin:3px 0;font-size:0.83rem;
                            display:flex;justify-content:space-between;align-items:center">
                    <span style="color:#e6edf3">{extra}</span>
                    <span style="color:#8b949e;font-size:0.75rem">{n_esc} escenas</span>
                </div>
                """, unsafe_allow_html=True)
            if len(p_e) > 25:
                st.caption(f"+ {len(p_e)-25} extras adicionales incluidos automáticamente")

        st.session_state.char_selected = char_selected

    with tab2:
        st.markdown('<div class="card-title">Escenas detectadas en el guion</div>', unsafe_allow_html=True)

        import pandas as pd
        data = []
        for e in escenas:
            data.append({
                "ESC": e.numero,
                "DÍA RODAJE": e.dia_rodaje,
                "LOCACIÓN": e.locacion,
                "EXT": "✓" if e.es_exterior else "",
                "INT": "✓" if e.es_interior else "",
                "DÍA": "✓" if e.es_dia else "",
                "NOC": "✓" if e.es_noche else "",
                "PERSONAJES": ", ".join(e.personajes[:4]) + ("..." if len(e.personajes) > 4 else ""),
            })
        df = pd.DataFrame(data)

        filtro_char = st.selectbox(
            "Filtrar por personaje",
            ["(Todos)"] + p_p,
            key="filtro_escenas"
        )
        if filtro_char != "(Todos)":
            df_filtrado = df[df["PERSONAJES"].str.contains(filtro_char, na=False)]
        else:
            df_filtrado = df

        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=420,
            column_config={
                "ESC": st.column_config.TextColumn("ESC", width=60),
                "DÍA RODAJE": st.column_config.TextColumn("DÍA RODAJE", width=130),
                "LOCACIÓN": st.column_config.TextColumn("LOCACIÓN", width=280),
                "EXT": st.column_config.TextColumn("EXT", width=50),
                "INT": st.column_config.TextColumn("INT", width=50),
                "DÍA": st.column_config.TextColumn("DÍA", width=50),
                "NOC": st.column_config.TextColumn("NOC", width=50),
                "PERSONAJES": st.column_config.TextColumn("PERSONAJES", width=220),
            },
            hide_index=True,
        )
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} escenas")

    with tab3:
        st.markdown('<div class="card-title">Vista previa del desglose por personaje</div>', unsafe_allow_html=True)

        char_preview = st.selectbox(
            "Seleccionar personaje",
            p_p,
            key="preview_char"
        )

        if char_preview and char_preview in breakdown.get('personajes', {}):
            char_data = breakdown['personajes'][char_preview]
            for dia, filas in char_data.items():
                st.markdown(f"""
                <div style="background:linear-gradient(90deg,#1B3A4B,#161b22);
                            border-left:3px solid #C9A84C;border-radius:0 6px 6px 0;
                            padding:8px 16px;margin:16px 0 8px 0;
                            font-weight:600;color:#C9A84C;font-size:0.9rem;
                            letter-spacing:0.5px">{dia}</div>
                """, unsafe_allow_html=True)
                for fila in filas:
                    ei = "🌿 EXT" if fila.ext else "🏠 INT"
                    dn = "🌙 NOC" if fila.noche else ("☀️ DÍA" if fila.dia else "")
                    obs = str(fila.observacion)
                    obs_preview = obs[:300] + ('...' if len(obs) > 300 else '')
                    st.markdown(f"""
                    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;
                                padding:12px 16px;margin:4px 0">
                        <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;flex-wrap:wrap">
                            <span style="background:#1B3A4B;color:#C9A84C;border:1px solid #4A6FA5;
                                        border-radius:4px;padding:2px 10px;font-family:monospace;
                                        font-size:0.82rem;font-weight:700">ESC {fila.escena}</span>
                            <span style="color:#8b949e;font-size:0.8rem">{ei}</span>
                            <span style="color:#8b949e;font-size:0.8rem">{dn}</span>
                            <span style="color:#8b949e;font-size:0.8rem;flex:1;min-width:120px">{fila.locacion[:50]}</span>
                            <span style="background:#FFF3CD20;color:#C9A84C;border:1px solid #C9A84C40;
                                        border-radius:4px;padding:2px 8px;font-size:0.75rem;font-weight:600">K{fila.kbio}</span>
                        </div>
                        <div style="color:#8b949e;font-size:0.82rem;line-height:1.5">{obs_preview}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="card-title">💾 Exportar Excel de desglose</div>', unsafe_allow_html=True)

    col_exp, col_reset = st.columns([3, 1], gap="large")

    with col_exp:
        char_selected = st.session_state.get('char_selected', {p: True for p in p_p})
        personajes_sel = [p for p, v in char_selected.items() if v]

        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;
                    padding:14px 18px;margin-bottom:16px">
            <div style="color:#8b949e;font-size:0.82rem;margin-bottom:8px">Se generará con:</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px">
                {''.join(f'<span class="char-badge">{p}</span>' for p in personajes_sel)}
            </div>
            <div style="color:#8b949e;font-size:0.78rem;margin-top:8px">
                + pestaña EXTRAS Y FIGURANTES + pestaña CAMBIOS
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬇️  Generar y descargar Excel", type="primary", key="btn_export"):
            if not personajes_sel:
                st.warning("Selecciona al menos un personaje.")
            else:
                with st.spinner("Generando Excel..."):
                    from app.core import excel_writer

                    bd_filtrado = {
                        'personajes': {p: v for p, v in breakdown['personajes'].items() if p in personajes_sel},
                        'extras': breakdown.get('extras', {}),
                        'cambios': [c for c in breakdown.get('cambios', []) if c['personaje'] in personajes_sel],
                    }

                    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                        out_path = tmp.name

                    excel_writer.write_excel(bd_filtrado, out_path)

                    with open(out_path, 'rb') as f:
                        xlsx_bytes = f.read()
                    os.unlink(out_path)

                filename = f"{st.session_state.pdf_name}_desglose.xlsx"
                st.download_button(
                    label="📥  Descargar Excel",
                    data=xlsx_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )
                st.success(f"✓ Excel listo — {len(xlsx_bytes)/1024:.0f} KB")

    with col_reset:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("↩  Nuevo guion", type="secondary", key="btn_reset"):
            for key in ['step', 'escenas', 'personajes_p', 'personajes_e', 'breakdown', 'pdf_name', 'pdf_bytes']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
