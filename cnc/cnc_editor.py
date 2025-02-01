import sys
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QLineEdit, QPushButton, QDialog, QLabel
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
class CNCEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Fő widget és layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Szövegszerkesztő létrehozása
        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Courier", 12, QFont.Bold))  # Monospace betűtípus
        layout.addWidget(self.text_edit)

        # Szintaxiskiemelő bekapcsolása
        self.highlighter = CNCHighlighter(self.text_edit.document())

        # 🔥 Háttérszín és szöveg szín beállítása
        self.setStyleSheet("background-color: #2E2E2E; color: #E0E0E0;")
        self.text_edit.setStyleSheet("background-color: #2E2E2E; color: #E0E0E0; border: none;")

        # Menü létrehozása
        menu = self.menuBar()

        # Fájl menü
        file_menu = menu.addMenu("Fájl")


        # Megnyitás gomb
        open_action = QAction("Megnyitás", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Mentés gomb
        save_action = QAction("Mentés", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Szerkesztés menü
        edit_menu = menu.addMenu("Szerkesztés")

        self.line_numbering_enabled = False  # Alapértelmezésben kikapcsolva

        toggle_numbers_action = QAction("Sorszámozás be/ki", self)
        toggle_numbers_action.triggered.connect(self.toggle_line_numbers)
        edit_menu.addAction(toggle_numbers_action)

        toggle_theme_action = QAction("Éjszakai/Nappali mód", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        edit_menu.addAction(toggle_theme_action)

        # Swap menüpont hozzáadása
        swap_action = QAction("Swap", self)
        swap_action.triggered.connect(self.open_swap_dialog)
        edit_menu.addAction(swap_action)

        #Nyelvek
        self.languages = {
            "hu": {"file": "Fájl", "edit": "Szerkesztés", "open": "Megnyitás", "save": "Mentés", "swap": "Swap",
                   "numbering": "Sorszámozás be/ki"},
            "en": {"file": "File", "edit": "Edit", "open": "Open", "save": "Save", "swap": "Swap",
                   "numbering": "Toggle Line Numbers"},
            "nl": {"file": "Bestand", "edit": "Bewerken", "open": "Openen", "save": "Opslaan", "swap": "Wisselen",
                   "numbering": "Regelnummering aan/uit"},
        }
        self.current_language = "hu"

        lang_menu = menu.addMenu("Languages")
        hu_action = QAction("Magyar", self)
        en_action = QAction("English", self)
        nl_action = QAction("Nederlands", self)

        hu_action.triggered.connect(lambda: self.set_language("hu"))
        en_action.triggered.connect(lambda: self.set_language("en"))
        nl_action.triggered.connect(lambda: self.set_language("nl"))

        lang_menu.addAction(hu_action)
        lang_menu.addAction(en_action)
        lang_menu.addAction(nl_action)

        # Ablak beállítások
        self.setWindowTitle("Cnc Coder by Spoiler")
        self.resize(800, 600)

        self.dark_mode = True  # Alapértelmezésben sötét mód

        self.dark_theme = """
            background-color: #2E2E2E;
            color: #E0E0E0;
        """

        self.light_theme = """
            background-color: #FFFFFF;
            color: #000000;
        """
        self.recent_files = []

    def open_swap_dialog(self):
        """Megnyitja a Swap ablakot"""
        dialog = SwapDialog(self)
        dialog.exec_()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fájl megnyitása", "",
                                                   "G-kód fájlok (*.nc *.gcode *.hyu);;Minden fájl (*.*)")
        if file_name:
            with open(file_name, "r") as file:
                self.text_edit.setText(file.read())
            self.setWindowTitle(f"CNC Coder by Spoiler - {file_name.split('/')[-1]}")

            # 📌 Hozzáadjuk a listához
            if file_name not in self.recent_files:
                self.recent_files.insert(0, file_name)
            if len(self.recent_files) > 5:
                self.recent_files.pop()

            self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Frissíti a legutóbb megnyitott fájlok listáját a menüben"""
        self.recent_files_menu.clear()
        for file_name in self.recent_files:
            action = QAction(file_name, self)
            action.triggered.connect(lambda checked, f=file_name: self.load_recent_file(f))
            self.recent_files_menu.addAction(action)

    def load_recent_file(self, file_name):
        """Megnyit egy korábban megnyitott fájlt"""
        with open(file_name, "r") as file:
            self.text_edit.setText(file.read())
        self.setWindowTitle(f"CNC Coder by Spoiler - {file_name.split('/')[-1]}")


    def toggle_theme(self):
        """Váltás éjszakai és nappali mód között"""
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.setStyleSheet(self.dark_theme)
            self.text_edit.setStyleSheet(self.dark_theme + "border: none;")
        else:
            self.setStyleSheet(self.light_theme)
            self.text_edit.setStyleSheet(self.light_theme + "border: none;")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fájl megnyitása", "",
                                                   "G-kód fájlok (*.nc *.gcode *.hyu);;Minden fájl (*.*)")
        if file_name:
            with open(file_name, "r") as file:
                self.text_edit.setText(file.read())
            self.setWindowTitle(f"CNC Coder by Spoiler - {file_name.split('/')[-1]}")  # 🔥 Cím frissítése


    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Fájl mentése", "",
                                                   "G-kód fájlok (*.nc *.gcode *.hyu);;Minden fájl (*.*)")
        if file_name:
            with open(file_name, "w") as file:
                file.write(self.text_edit.toPlainText())
            self.setWindowTitle(f"CNC Coder by Spoiler - {file_name.split('/')[-1]}")  # 🔥 Cím frissítése)

        if file_name:
            lines = self.text_edit.toPlainText().upper().split("\n")  # 💡 Mentés nagybetűsen

            # Ellenőrizzük, hogy az első sor megfelelő-e (pl. O1234%)
            if not re.match(r"^O\d+%$", lines[0].strip()):
                QMessageBox.warning(self, "Hiba", "A program neve kötelező (pl. O1234%)!")
                return

            # EOB (;) minden sor végére
            new_lines = [line.strip() + ";" if not line.strip().endswith(";") else line.strip() for line in lines]

            # M30 után tegyünk egy "%"-ot
            if "M30" in new_lines[-1]:
                new_lines.append("%")

            # 📌 Fájl mentése
            with open(file_name, "w") as file:
                file.write("\n".join(new_lines))

    def insert_line_numbers(self):
        """Sorszámozás beillesztése minden sor elejére"""
        text = self.text_edit.toPlainText()
        lines = text.split("\n")

        # Megjegyezzük a kurzor pozícióját
        cursor = self.text_edit.textCursor()
        position = cursor.position()

        # Újraszámozott sorok
        new_lines = [f"N{index + 1} {line}" if not line.strip().startswith("N") else line for index, line in
                     enumerate(lines)]
        self.text_edit.setPlainText("\n".join(new_lines))

        # Visszaállítjuk a kurzort az eredeti helyre
        cursor.setPosition(position)
        self.text_edit.setTextCursor(cursor)

    def toggle_line_numbers(self):
        """Be- vagy kikapcsolja a sorszámozást"""
        self.line_numbering_enabled = not self.line_numbering_enabled
        if self.line_numbering_enabled:
            self.insert_line_numbers()
        else:
            # Eltávolítjuk a sorszámozást
            text = self.text_edit.toPlainText()
            new_lines = [re.sub(r"^N\d+\s*", "", line) for line in text.split("\n")]
            self.text_edit.setPlainText("\n".join(new_lines))

    def set_language(self, lang):
        """Beállítja a nyelvet"""
        self.current_language = lang
        self.menuBar().clear()

        menu = self.menuBar()
        file_menu = menu.addMenu(self.languages[lang]["file"])
        edit_menu = menu.addMenu(self.languages[lang]["edit"])
        lang_menu = menu.addMenu("Languages")

        # Új menüelemek
        open_action = QAction(self.languages[lang]["open"], self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(self.languages[lang]["save"], self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        swap_action = QAction(self.languages[lang]["swap"], self)
        swap_action.triggered.connect(self.open_swap_dialog)
        edit_menu.addAction(swap_action)

        toggle_numbers_action = QAction(self.languages[lang]["numbering"], self)
        toggle_numbers_action.triggered.connect(self.toggle_line_numbers)
        edit_menu.addAction(toggle_numbers_action)

        # Nyelvváltó menü visszahelyezése
        hu_action = QAction("Magyar", self)
        en_action = QAction("English", self)
        nl_action = QAction("Nederlands", self)

        hu_action.triggered.connect(lambda: self.set_language("hu"))
        en_action.triggered.connect(lambda: self.set_language("en"))
        nl_action.triggered.connect(lambda: self.set_language("nl"))

        lang_menu.addAction(hu_action)
        lang_menu.addAction(en_action)
        lang_menu.addAction(nl_action)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Kilépés", "Biztosan kilépsz mentés nélkül?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class SwapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Szövegcsere (Swap)")
        self.resize(300, 150)

        layout = QVBoxLayout()

        # In mező (keresendő szöveg)
        self.in_label = QLabel("In (keresendő):")
        layout.addWidget(self.in_label)
        self.in_field = QLineEdit()
        layout.addWidget(self.in_field)

        # Out mező (csere)
        self.out_label = QLabel("Out (csere):")
        layout.addWidget(self.out_label)
        self.out_field = QLineEdit()
        layout.addWidget(self.out_field)

        # Swap gomb
        self.swap_button = QPushButton("Cserélés")
        self.swap_button.clicked.connect(self.swap_text)
        layout.addWidget(self.swap_button)

        self.setLayout(layout)

    def swap_text(self):
        in_text = self.in_field.text()
        out_text = self.out_field.text()

        if not in_text:
            return  # Ha üres az In mező, ne csináljon semmit

        # Szöveg cseréje a fő szövegablakban
        parent = self.parent()
        if parent and isinstance(parent, CNCEditor):
            content = parent.text_edit.toPlainText()
            new_content = content.replace(in_text, out_text)
            parent.text_edit.setText(new_content)

        self.close()  # Ablak bezárása csere után

class CNCHighlighter(QSyntaxHighlighter):
    """G-kód szintaxiskiemelő"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []

        self.add_rule(r'\bG\d*\b', QColor("#4DA6FF"))  # G-kód és közvetlen utána lévő számok: világoskék
        self.add_rule(r'\bM\d*\b', QColor("#FF6666"))  # M-kód és közvetlen utána lévő számok: világos piros
        self.add_rule(r'\bO\d+\b', QColor("#80FF80"))  # O-kód (program kezdet): világoszöld
        self.add_rule(r'\b[XYZIJKRFS]-?\d*\.?\d+\b', QColor("#FFFF99"))  # Koordináták sárgán (negatív is)

    def add_rule(self, pattern, color):
        """Szabály hozzáadása a szintaxiskiemeléshez"""
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        self.rules.append((re.compile(pattern), fmt))

    def highlightBlock(self, text):
        """Szöveg kiemelése"""
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

# Program indítása
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CNCEditor()
    editor.show()
    sys.exit(app.exec_())