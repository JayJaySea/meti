#!/usr/bin/env python3

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from sys import argv
import os
import shutil
from meti.gui.window import MainWindow
from meti import data
from meti.data import DATA_DIR

def main():
    data.init()
    app = QApplication(argv)

    with open(os.path.join(DATA_DIR, "style.css")) as style:
        app.setStyleSheet(style.read())

    font_path = os.path.join(DATA_DIR, "fonts", "Rajdhani-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)

    font_path = os.path.join(DATA_DIR, "fonts", "Orbitron-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)

    font_path = os.path.join(DATA_DIR, "fonts", "RobotoMono-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
