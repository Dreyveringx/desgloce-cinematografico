"""
Script de construcción de la aplicación instalable.
Ejecutar: python build_app.py

Genera:
- Windows: dist/ScriptBreakerPro/ScriptBreakerPro.exe (+ carpeta de dependencias)
- Mac: dist/ScriptBreakerPro.app
- Para distribuir: comprimir la carpeta dist/ como .zip
"""
import os
import subprocess
import sys


def build():
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

    app_name = "ScriptBreakerPro"
    entry = "main.py"

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',
        '--windowed',
        f'--name={app_name}',
        '--clean',
        '--noconfirm',
        '--hidden-import=pdfplumber',
        '--hidden-import=openpyxl',
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=app.core.pdf_reader',
        '--hidden-import=app.core.script_parser',
        '--hidden-import=app.core.breakdown_builder',
        '--hidden-import=app.core.excel_writer',
        '--hidden-import=app.ui.main_window',
        '--collect-data=customtkinter',
        '--collect-data=pdfplumber',
        entry,
    ]

    icon_path = os.path.join('assets', 'icon.ico')
    if os.path.exists(icon_path):
        cmd += [f'--icon={icon_path}']

    subprocess.run(cmd, check=True)

    print()
    print("=" * 50)
    print("CONSTRUCCIÓN EXITOSA")
    print("=" * 50)
    if sys.platform == 'win32':
        print(f"Ejecutable: dist/{app_name}/{app_name}.exe")
        print("Para distribuir: comprime la carpeta dist/ completa como .zip")
    elif sys.platform == 'darwin':
        print(f"App: dist/{app_name}.app")
        print("Para distribuir: comprime dist/ScriptBreakerPro.app como .zip")
    print()


if __name__ == '__main__':
    build()
