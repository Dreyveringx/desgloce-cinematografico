import os
import threading
from tkinter import filedialog

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_MAIN = "#1a1a2e"
BG_PANEL = "#0f3460"
BG_CARD = "#16213e"
ACCENT = "#f0a500"
SUCCESS = "#27ae60"
DANGER = "#e94560"
TEXT_PRI = "#e0e0e0"
TEXT_SEC = "#888888"


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ScriptBreaker Pro")
        self.geometry("1180x740")
        self.minsize(900, 600)
        self.configure(fg_color=BG_MAIN)
        self.pdf_path = None
        self.breakdown_data = None
        self.all_escenas = []
        self.personajes_detectados = []
        self.char_vars = {}
        self._build_ui()
        self.after(100, self._center_window)
        self._setup_drag_drop()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _show_error(self, msg):
        import tkinter.messagebox as mb
        mb.showerror(
            "Error en el análisis",
            f"Ocurrió un problema al analizar el PDF:\n\n{msg}\n\n"
            "Asegúrate de que el PDF sea un guion en formato estándar.\n"
            "Si el error persiste, intenta con otro PDF."
        )

    def _open_file(self, path):
        import subprocess
        import sys
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path], check=False)
            else:
                subprocess.run(['xdg-open', path], check=False)
        except Exception:
            pass

    def _setup_drag_drop(self):
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD  # noqa: F401
        except ImportError:
            pass

    def _build_ui(self):
        self.left = ctk.CTkFrame(self, width=290, fg_color=BG_PANEL, corner_radius=12)
        self.left.pack(side="left", fill="y", padx=12, pady=12)
        self.left.pack_propagate(False)

        ctk.CTkLabel(self.left, text="🎬 ScriptBreaker Pro",
                     font=ctk.CTkFont("Helvetica", 17, "bold"),
                     text_color=ACCENT).pack(pady=(22, 4))
        ctk.CTkLabel(self.left, text="Desglose de producción cinematográfica",
                     font=ctk.CTkFont(size=10), text_color=TEXT_SEC,
                     wraplength=250).pack(pady=(0, 16))

        drop = ctk.CTkFrame(self.left, height=100, fg_color=BG_MAIN,
                            corner_radius=10, border_width=2, border_color=ACCENT)
        drop.pack(fill="x", padx=14, pady=(0, 10))
        drop.pack_propagate(False)
        ctk.CTkLabel(drop, text="📄  Arrastra tu PDF aquí",
                     font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(expand=True)

        ctk.CTkButton(self.left, text="Abrir PDF", height=36,
                      fg_color=ACCENT, text_color=BG_MAIN, hover_color="#d4920a",
                      font=ctk.CTkFont(weight="bold"),
                      command=self.open_pdf).pack(fill="x", padx=14, pady=(0, 8))

        self.file_label = ctk.CTkLabel(self.left, text="Sin archivo cargado",
                                       font=ctk.CTkFont(size=10), text_color=TEXT_SEC,
                                       wraplength=260)
        self.file_label.pack(pady=(0, 12))

        ctk.CTkFrame(self.left, height=1, fg_color=BG_MAIN).pack(fill="x", padx=14)

        self.progress_label = ctk.CTkLabel(self.left, text="",
                                           font=ctk.CTkFont(size=10), text_color=TEXT_SEC)
        self.progress_label.pack(pady=(12, 3))
        self.progress_bar = ctk.CTkProgressBar(self.left, fg_color=BG_MAIN,
                                               progress_color=ACCENT, height=8)
        self.progress_bar.pack(fill="x", padx=14)
        self.progress_bar.set(0)

        ctk.CTkFrame(self.left, height=1, fg_color=BG_MAIN).pack(fill="x", padx=14, pady=12)

        self.btn_analyze = ctk.CTkButton(self.left, text="🔍  Analizar guion",
                                         height=40, fg_color=DANGER,
                                         text_color="white", hover_color="#c0392b",
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         state="disabled", command=self.start_analysis)
        self.btn_analyze.pack(fill="x", padx=14, pady=(0, 4))

        self.analyze_hint = ctk.CTkLabel(
            self.left, text="Primero carga un PDF",
            font=ctk.CTkFont(size=9), text_color=TEXT_SEC)
        self.analyze_hint.pack(padx=14, pady=(0, 8))

        self.stats_label = ctk.CTkLabel(self.left, text="",
                                        font=ctk.CTkFont(size=10), text_color=TEXT_SEC,
                                        justify="left")
        self.stats_label.pack(padx=14, pady=4)

        self.btn_export = ctk.CTkButton(self.left, text="💾  Generar Excel",
                                        height=46, fg_color=SUCCESS,
                                        text_color="white", hover_color="#219a52",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        state="disabled", command=self.export_excel)
        self.btn_export.pack(fill="x", padx=14, pady=14, side="bottom")

        self.right = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        self.right.pack(side="right", fill="both", expand=True, padx=(0, 12), pady=12)

        self.tabs = ctk.CTkTabview(self.right, fg_color=BG_MAIN,
                                   segmented_button_fg_color=BG_PANEL,
                                   segmented_button_selected_color=ACCENT,
                                   segmented_button_selected_hover_color="#d4920a",
                                   text_color=TEXT_PRI)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=8)
        self.tabs.add("Personajes")
        self.tabs.add("Escenas")

        self.chars_frame = ctk.CTkScrollableFrame(
            self.tabs.tab("Personajes"), fg_color="transparent")
        self.chars_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.chars_frame,
                     text="Carga un PDF para detectar los personajes",
                     text_color=TEXT_SEC, font=ctk.CTkFont(size=12)).pack(pady=40)

        self.scenes_frame = ctk.CTkScrollableFrame(
            self.tabs.tab("Escenas"), fg_color="transparent")
        self.scenes_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.scenes_frame,
                     text="Las escenas aparecerán aquí tras el análisis",
                     text_color=TEXT_SEC, font=ctk.CTkFont(size=12)).pack(pady=40)

    def open_pdf(self):
        path = filedialog.askopenfilename(
            title="Seleccionar guion PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")]
        )
        if not path:
            return
        self.pdf_path = path
        name = os.path.basename(path)
        self.file_label.configure(text=name, text_color=ACCENT)
        self.btn_analyze.configure(state="normal")
        self.analyze_hint.configure(text="")
        self.progress_bar.set(0)
        self.progress_label.configure(text="")

    def _update_progress(self, msg, val):
        self.after(0, lambda: self.progress_label.configure(text=msg))
        self.after(0, lambda: self.progress_bar.set(val))

    def start_analysis(self):
        if not self.pdf_path:
            return
        self.btn_analyze.configure(state="disabled")
        self.btn_export.configure(state="disabled")

        def run():
            try:
                from app.core import breakdown_builder, pdf_reader, script_parser

                self._update_progress("Extrayendo texto del PDF...", 0.15)
                text = pdf_reader.extract_text(self.pdf_path)

                self._update_progress("Detectando escenas...", 0.35)
                escenas = script_parser.parse_scenes(text)

                self._update_progress("Identificando personajes...", 0.55)
                p_principales, p_extras = script_parser.detect_characters(text, escenas)
                escenas = script_parser.assign_shooting_days(escenas)
                script_parser.calculate_kbio(escenas, p_principales)

                self._update_progress("Construyendo desglose...", 0.80)
                self.breakdown_data = breakdown_builder.build(escenas, p_principales, p_extras)
                self.all_escenas = escenas
                self.personajes_detectados = p_principales

                self._update_progress("✓ Análisis completado", 1.0)
                self.after(0, self._on_done)
            except Exception as e:
                import traceback
                err_msg = str(e)
                self._update_progress(f"Error: {err_msg}", 0)
                print(traceback.format_exc())
                self.after(0, lambda: self.btn_analyze.configure(state="normal"))
                self.after(0, lambda: self._show_error(err_msg))

        threading.Thread(target=run, daemon=True).start()

    def _on_done(self):
        self.btn_export.configure(state="normal")
        self.btn_analyze.configure(state="normal")
        n_esc = len(self.all_escenas)
        n_per = len(self.personajes_detectados)
        n_dias = len(set(e.dia_rodaje for e in self.all_escenas))
        self.stats_label.configure(
            text=f"{n_esc} escenas  ·  {n_per} personajes\n{n_dias} días de rodaje",
            text_color=TEXT_PRI)
        self._populate_chars()
        self._populate_scenes()

    def _populate_chars(self):
        for w in self.chars_frame.winfo_children():
            w.destroy()
        self.char_vars = {}
        ctk.CTkLabel(self.chars_frame, text="Personajes principales",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", padx=12, pady=(12, 6))
        for char in self.personajes_detectados:
            n = sum(1 for e in self.all_escenas if char in e.personajes)
            var = ctk.BooleanVar(value=True)
            self.char_vars[char] = var
            row = ctk.CTkFrame(self.chars_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkCheckBox(row, text=char, variable=var,
                            text_color=TEXT_PRI, fg_color=ACCENT,
                            hover_color="#d4920a", checkmark_color=BG_MAIN).pack(side="left")
            ctk.CTkLabel(row, text=f"{n} esc.",
                         font=ctk.CTkFont(size=10), text_color=TEXT_SEC).pack(side="right")

    def _populate_scenes(self):
        for w in self.scenes_frame.winfo_children():
            w.destroy()
        hdr = ctk.CTkFrame(self.scenes_frame, fg_color=BG_PANEL)
        hdr.pack(fill="x", padx=4, pady=(4, 0))
        for txt, w in [("ESC", 55), ("LOCACION", 280), ("E/I", 45), ("D/N", 45), ("PERSONAJES", 220)]:
            ctk.CTkLabel(hdr, text=txt, width=w, anchor="w",
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=ACCENT).pack(side="left", padx=4, pady=5)
        for i, esc in enumerate(self.all_escenas[:200]):
            bg = BG_CARD if i % 2 == 0 else BG_MAIN
            row = ctk.CTkFrame(self.scenes_frame, fg_color=bg)
            row.pack(fill="x", padx=4, pady=1)
            ei = "EXT" if esc.es_exterior else "INT"
            dn = "NOC" if esc.es_noche else ("DIA" if esc.es_dia else "---")
            pers = ", ".join(esc.personajes[:3])
            for txt, w, color in [
                (esc.numero, 55, ACCENT),
                (esc.locacion[:38], 280, TEXT_PRI),
                (ei, 45, "#74b9ff" if esc.es_exterior else "#a29bfe"),
                (dn, 45, "#fdcb6e" if esc.es_dia else "#636e72"),
                (pers[:28], 220, TEXT_SEC),
            ]:
                ctk.CTkLabel(row, text=txt, width=w, anchor="w",
                             font=ctk.CTkFont(size=10), text_color=color).pack(side="left", padx=4, pady=3)

    def export_excel(self):
        if not self.breakdown_data:
            return
        sel = [p for p, v in self.char_vars.items() if v.get()]
        bd_filtrado = {
            'personajes': {p: v for p, v in self.breakdown_data['personajes'].items() if p in sel},
            'extras': self.breakdown_data.get('extras', {}),
            'cambios': [c for c in self.breakdown_data.get('cambios', []) if c['personaje'] in sel],
        }
        pdf_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        output = filedialog.asksaveasfilename(
            title="Guardar desglose Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"{pdf_name}_desglose.xlsx"
        )
        if not output:
            return
        self._update_progress("Generando Excel...", 0.5)

        def run():
            from app.core import excel_writer
            try:
                excel_writer.write_excel(bd_filtrado, output)
                self.after(0, lambda: self._update_progress("✓ Excel guardado", 1.0))
                self.after(0, lambda: self._open_file(output))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=run, daemon=True).start()
