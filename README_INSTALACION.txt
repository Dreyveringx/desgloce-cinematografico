SCRIPTBREAKER — GUÍA DE INSTALACIÓN
=========================================

OPCIÓN 1 — SIN INSTALAR NADA (recomendada si ya tienes Python)
---------------------------------------------------------------
Windows: Doble clic en "install_and_run.bat"
Mac/Linux: Doble clic en "install_and_run.command"
  (en Mac, si pide permiso: clic derecho > Abrir)

OPCIÓN 2 — CREAR APLICACIÓN EJECUTABLE (para distribuir)
---------------------------------------------------------
Requiere tener Python instalado con pip.

1. Abrir terminal en la carpeta del proyecto
2. Ejecutar: python build_app.py
3. El ejecutable quedará en la carpeta "dist/"
4. Comprimir la carpeta "dist/" como .zip para distribuir

OPCIÓN 3 — EJECUTAR DIRECTAMENTE (si ya tienes Python y las librerías)
----------------------------------------------------------------------
Abrir terminal en la carpeta del proyecto y ejecutar:
  python main.py

REQUISITOS MÍNIMOS
-----------------
- Windows 10/11, macOS 11+, o Ubuntu 20.04+
- Python 3.10 o superior (si usas Opción 1 o 2)
- 200 MB de espacio libre

USO DE LA APLICACIÓN
--------------------
1. Abrir la aplicación
2. Clic en "Abrir PDF" y seleccionar el guion
3. Clic en "Analizar guion" (puede tardar 10-30 segundos según tamaño)
4. Revisar los personajes detectados (marcar/desmarcar con los checkbox)
5. Clic en "Generar Excel" y elegir dónde guardar
6. ¡Listo! Abrir el Excel generado

OPCIÓN 4 — INTERFAZ WEB (navegador, PC o celular en la misma WiFi)
------------------------------------------------------------------
Windows: Doble clic en "run_web.bat"
Mac/Linux: Doble clic en "run_web.command"
Luego abre http://localhost:8501 en el navegador.

ACCESO DESDE CELULAR O TABLET (por WiFi)
-----------------------------------------
1. Asegúrate de que tu celular/tablet esté en la misma red WiFi que el computador
2. En el computador: ejecuta "run_web.bat" (Windows) o "run_web.command" (Mac)
3. Busca la IP de tu computador:
   - Windows: abre CMD y escribe "ipconfig" → busca "Dirección IPv4"
   - Mac: abre Terminal y escribe "ipconfig getifaddr en0"
   - Ejemplo de IP: 192.168.1.105
4. En el celular/tablet: abre el navegador y escribe:
   http://192.168.1.105:8501
5. ¡Listo! La app se abre en el navegador del celular/tablet

SOPORTE
-------
Si la app no abre o hay un error, asegúrate de tener
Python 3.10+ instalado desde: https://www.python.org
