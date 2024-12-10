from PySide6.QtGui import (QColor, QSyntaxHighlighter, QTextCharFormat, QFont)
import re


class HighlighterPalette():
    def addHighlight(self, color_name, foreground, weight=QFont.Normal):
        new_color = QTextCharFormat()
        new_color.setForeground(foreground)
        new_color.setFontWeight(weight)
        setattr(self, color_name, new_color)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.palette = HighlighterPalette()
        # Gruvbox light scheme
        self.palette.addHighlight("red", QColor(204, 36, 29))
        self.palette.addHighlight("red_bold", QColor(204, 36, 29), QFont.Bold)
        self.palette.addHighlight("green", QColor(152, 151, 26))
        self.palette.addHighlight("yellow", QColor(215, 153, 33))
        self.palette.addHighlight("blue", QColor(69, 133, 136))
        self.palette.addHighlight("purple", QColor(177, 98, 134))
        self.palette.addHighlight("aqua", QColor(104, 157, 106))
        self.palette.addHighlight("orange", QColor(214, 93, 14))

        self._mappings = {
                r'DEFINITION:|CALL:': self.palette.red_bold,
                r'{|}|\(|\)|=': self.palette.orange,
                r',': self.palette.aqua,
                r'<-|\?': self.palette.green,
                }

    def highlightBlock(self, text):
        for pattern, format in self._mappings.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
