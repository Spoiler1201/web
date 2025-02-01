import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QFont
from cnc_highlighter import CNCHighlighter  # Szintaxiskiemelő importálása

class CNCEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Szövegszerkesztő létrehozása
        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Courier", 12))  # Monospace font
        self.setCentralWidget(self.text_edit)

        # Szintaxiskiemelő bekapcsolása
        self.highlighter = CNCHighlighter(self.text_edit.document())

        # Menü létrehozása
        menu = self.menuBar()
        file_menu = menu.addMenu("Fájl")

        # Megnyitás gomb
        open_action = QAction("Megnyitás", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Mentés gomb
        save_action = QAction("Mentés", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Ablak beállítások
        self.setWindowTitle("CNC Szövegszerkesztő")
        self.resize(800, 600)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fájl megnyitása", "", "G-kód fájlok (*.nc *.gcode);;Minden fájl (*.*)")
        if file_name:
            with open(file_name, "r") as file:
                self.text_edit.setText(file.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Fájl mentése", "", "G-kód fájlok (*.nc *.gcode);;Minden fájl (*.*)")
        if file_name:
            with open(file_name, "w") as file:
                file.write(self.text_edit.toPlainText())

# Program indítása
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CNCEditor()
    editor.show()
    sys.exit(app.exec_())