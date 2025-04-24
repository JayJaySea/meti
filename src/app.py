from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from sys import argv
from gui.window import MainWindow
import data
from data import DATA_DIR
import os


def main():
    data.setup_data_dir()
    app = QApplication(argv)

    with open(os.path.join(DATA_DIR, "style.css")) as style:
        app.setStyleSheet(style.read())

    font_path = os.path.join(DATA_DIR, "fonts", "rajdhani", "Rajdhani-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)

    font_path = os.path.join(DATA_DIR, "fonts", "orbitron", "static", "Orbitron-Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()

