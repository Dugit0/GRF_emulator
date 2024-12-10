"""
Based on
https://stackoverflow.com/questions/76223711/fixing-pyqt-textedit-line-number-counter-and-weird-status-bar-error
"""

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QEvent


class LineCountTextEdit(QTextEdit):
    lineCount = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.updateLineNumbers)
        self.verticalScrollBar().rangeChanged.connect(self.update)
        self.verticalScrollBar().valueChanged.connect(self.update)

    def event(self, event):
        if event.type() == QEvent.Paint:
            # we cannot override paintEvent(), because it has effect on the
            # viewport and we need to directly paint on the widget.
            super().event(event)
            self.paintLineNumbers()
            return True
        return super().event(event)

    def paintLineNumbers(self):
        qp = QPainter(self)
        fm = self.fontMetrics()
        margins = self.contentsMargins()
        left = margins.left()
        viewMargin = self.viewportMargins().left()
        rightMargin = viewMargin - (fm.horizontalAdvance(' ') + left)

        viewTop = margins.top()
        viewHeight = self.height() - (viewTop + margins.bottom())
        qp.setClipRect(
            viewTop, margins.left(),
            viewMargin, viewHeight
        )
        qp.translate(margins.left(), 0)

        top = self.verticalScrollBar().value()
        bottom = top + viewHeight
        offset = viewTop - self.verticalScrollBar().value()
        lineCount = 1
        doc = self.document()
        docLayout = doc.documentLayout()
        block = doc.begin()

        while block.isValid():
            blockRect = docLayout.blockBoundingRect(block)
            blockTop = blockRect.y()
            blockLayout = block.layout()
            blockLineCount = blockLayout.lineCount()
            if (
                blockRect.bottom() >= top
                and blockTop + offset <= bottom
            ):
                # only draw a text block if its bounding rect is visible
                for l in range(blockLineCount):
                    line = blockLayout.lineAt(l)
                    qp.drawText(
                        left, offset + blockTop + line.y(),
                        rightMargin, line.height(),
                        Qt.AlignRight, str(lineCount)
                    )
                    lineCount += 1
            else:
                lineCount += blockLineCount

            block = block.next()

    def updateLineNumbers(self):
        lineCount = 0
        block = self.document().begin()
        while block.isValid():
            lineCount += block.layout().lineCount()
            block = block.next()
        if lineCount < 1:
            lineCount = 1

        if self.lineCount != lineCount:
            self.lineCount = lineCount
            countLength = len(str(self.lineCount))
            margin = self.fontMetrics().horizontalAdvance(
                    '  ' + '0' * countLength
                    )
            if self.viewportMargins().left() != margin:
                self.setViewportMargins(margin, 0, 0, 0)

        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateLineNumbers()
