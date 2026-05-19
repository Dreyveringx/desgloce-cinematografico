import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
    except Exception:
        pass
    app.mainloop()
