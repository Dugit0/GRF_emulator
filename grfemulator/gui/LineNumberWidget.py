"""
Based on


MIT License

Copyright (c) 2021 Jung Gyu Yoon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt


class LineNumberWidget(QTextBrowser):
    def __init__(self, widget):
        super().__init__()
        self.initUi(widget)

    def initUi(self, widget):
        self.lineCount = widget.document().lineCount()
        self.externFont = widget.font()
        self.initStyleSheet()
        self.setExternFont()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        self.verticalScrollBar().setEnabled(False)

        widget.verticalScrollBar().valueChanged.connect(self.changeSelfScroll)

        self.initLineCount()

    def changeSelfScroll(self, v):
        # Change LineWidget scroll as targeted widget scroll changed
        self.verticalScrollBar().setValue(v)

    def initLineCount(self):
        for n in range(1, self.lineCount + 1):
            self.append(str(n))

    def changeLineCount(self, n):
        max_one = max(self.lineCount, n)
        diff = n - self.lineCount
        if max_one == self.lineCount:
            first_v = self.verticalScrollBar().value()
            for i in range(self.lineCount, self.lineCount + diff, -1):
                self.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
                self.moveCursor(QTextCursor.StartOfLine,
                                QTextCursor.MoveAnchor)
                self.moveCursor(QTextCursor.End, QTextCursor.KeepAnchor)
                self.textCursor().removeSelectedText()
                self.textCursor().deletePreviousChar()
            last_v = self.verticalScrollBar().value()
            if abs(first_v - last_v) != 2:
                self.verticalScrollBar().setValue(first_v)
        else:
            for i in range(self.lineCount, self.lineCount + diff, 1):
                self.append(str(i + 1))
        self.lineCount = n

    def initStyleSheet(self):
        styleSheet = '''
                     QTextBrowser
                     {
                     background: transparent;
                     border: none;
                     color: #AAA;
                     }
                     '''
        self.setStyleSheet(styleSheet)
        self.setFixedWidth(self.externFont.pointSize() * 4)

    def setExternFont(self):
        self.setFont(self.externFont)
