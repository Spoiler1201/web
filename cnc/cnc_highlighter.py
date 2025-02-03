class CNCHighlighter(QSyntaxHighlighter):
    def __init__(self, document, dark_mode=False):  # 🔥 dark_mode most már egy opcionális paraméter
        super().__init__(document)
        self.dark_mode = dark_mode  # 🔥 Elmentjük a dark mode állapotát

        # Színek beállítása a témától függően
        self.number_color = QColor("#FFFFFF") if self.dark_mode else QColor("#000000")

        self.rules = []  # Szabályok listája
        self.add_rule(r'\b[XYZIJKRFS]-?\d*\.?\d+\b', self.number_color)  # Koordináták színe

        # Szabályos G-kódok és M-kódok
        self.valid_gcodes = {"G00", "G01", "G02", "G03", "G90", "G91"}
        self.valid_mcodes = {"M03", "M05", "M30"}

        # Színek beállítása
        self.gcode_format = QTextCharFormat()
        self.gcode_format.setForeground(QColor("blue"))
        self.gcode_format.setFontWeight(QFont.Bold)

        self.mcode_format = QTextCharFormat()
        self.mcode_format.setForeground(QColor("red"))
        self.mcode_format.setFontWeight(QFont.Bold)

        self.coord_format = QTextCharFormat()
        self.coord_format.setForeground(QColor("#FFFFFF") if self.dark_mode else QColor("#000000")

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("gray"))
        self.comment_format.setFontItalic(True)

        self.error_format = QTextCharFormat()
        self.error_format.setBackground(QColor("lightcoral"))  # Hibás sorok pirossal

    def highlightBlock(self, text):
        has_error = False  # Hibás sor nyomon követése

        # G-kódok színezése
        for match in re.finditer(r'\b(G\d+)\b', text):
            code = match.group(1)
            if code in self.valid_gcodes:
                self.setFormat(match.start(), match.end() - match.start(), self.gcode_format)
            else:
                has_error = True  # Hibás G-kód

        # M-kódok színezése
        for match in re.finditer(r'\b(M\d+)\b', text):
            code = match.group(1)
            if code in self.valid_mcodes:
                self.setFormat(match.start(), match.end() - match.start(), self.mcode_format)
            else:
                has_error = True  # Hibás M-kód

        # Koordináták (X, Y, Z, F, S) színezése
        for match in re.finditer(r'\b[XYZFS]-?\d+(\.\d+)?\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.coord_format)

        # Megjegyzések színezése (zárójelek között)
        for match in re.finditer(r'\(.*?\)', text):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_format)

        # Hibás sor teljes piros kiemelése
        if has_error:
            self.setFormat(0, len(text), self.error_format)