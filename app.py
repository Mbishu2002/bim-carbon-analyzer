"""Entry point for the BIM Embodied Carbon Analyzer (PySide6 desktop app).

Run with:
    python app.py
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src.*` imports resolve when this
# file is launched directly (e.g. PyCharm / double-click).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BIM Embodied Carbon Analyzer")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
