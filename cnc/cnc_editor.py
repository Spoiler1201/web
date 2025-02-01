import sys
from PyQt5.QtWidgets import QApplication, QTextEdit, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QFont
from cnc_highlighter import CNCHighlighter  # Szintaxiskiemelő importálása
from PyQt5.QtWidgets import QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QWidget

class CNCEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Fő widget és layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Szövegszerkesztő létrehozása
        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Courier", 12, QFont.Bold))  # Monospace
        self.setCentralWidget(self.text_edit)

        # Swap mezők
        self.in_field = QLineEdit(self)
        self.in_field.setPlaceholderText("In: Cserélendő szöveg")
        layout.addWidget(self.in_field)

        self.out_field = QLineEdit(self)
        self.out_field.setPlaceholderText("Out: Új szöveg (hagyja üresen a törléshez)")
        layout.addWidget(self.out_field)

        # Swap gomb
        swap_button = QPushButton("Swap", self)
        swap_button.clicked.connect(self.swap_text)
        layout.addWidget(swap_button)

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
        file_name, _ = QFileDialog.getSaveFileName(self, "Fájl mentése", "",
                                                   "G-kód fájlok (*.nc *.gcode);;Minden fájl (*.*)")
        if file_name:
            lines = self.text_edit.toPlainText().split("\n")

            # Ellenőrizzük, hogy az első sor megfelelő-e (pl. O1234%)
            if not re.match(r"^O\d+%$", lines[0].strip()):
                QMessageBox.warning(self, "Hiba", "A program neve kötelező (pl. O1234%)!")
                return

            # EOB (;) minden sor végére
            new_lines = [line.strip() + ";" if not line.strip().endswith(";") else line.strip() for line in lines]

            # M30 után tegyünk egy "%"-ot
            if "M30" in new_lines[-1]:
                new_lines.append("%")

            with open(file_name, "w") as file:
                file.write("\n".join(new_lines))

    def swap_text(self):
        """ Megkeresi és kicseréli az 'In' szöveget 'Out'-ra """
        in_text = self.in_field.text()
        out_text = self.out_field.text()

        if not in_text:
            QMessageBox.warning(self, "Hiba", "Add meg a cserélendő szöveget!")
            return


# Program indítása
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CNCEditor()
    editor.show()
    sys.exit(app.exec_())
