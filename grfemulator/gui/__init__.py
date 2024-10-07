from PySide6.QtGui import (QColor, QIcon, QAction, QFont, QFontDatabase,
                           QSyntaxHighlighter, QTextCharFormat)
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QDialog,
                               QVBoxLayout, QHBoxLayout, QPlainTextEdit,
                               QSplitter, QStatusBar, QToolBar, QLabel,
                               QCheckBox, QMessageBox, QFileDialog,
                               QDialogButtonBox)
from PySide6.QtCore import Qt
from .LineNumberWidget import LineNumberWidget
from .. import core
from . import darkorange
import re
import os
import sys

"""
TODO:
    setWindowTitle
    setWindowIcon
    QToolTip
    exitAction.setShortcut('Ctrl+Q')
    Filepath in statusbar
"""

# TODO use Path
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')

class MarkDebugDialog(QDialog):
    def __init__(self, parent, func_names):
        super().__init__()
        
        self.setWindowTitle("Functions for debugging")
        self.setWindowIcon(QIcon(LOGO_PATH))

        
        self.layout = QVBoxLayout()
        
        message = QLabel("Mark functions for debugging")
        self.layout.addWidget(message)
        
        self.checkboxes = [QCheckBox(name, self) for name in func_names]
        for checkbox in self.checkboxes:
            self.layout.addWidget(checkbox)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


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

class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None
        self.saved_text = ""
        self.debug_func_names = []

        self.setWindowIcon(QIcon(LOGO_PATH))
        self.setWindowTitle("GRF emulator")
        self.setGeometry(100, 100, 1200, 700)   # setting window geometry
        
        layout = QHBoxLayout()   # creating a layout

        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) # setting font to the editor
        fixedfont.setPointSize(12)
        
        # Main editor and line number widget
        self.editor = QPlainTextEdit()                                # creating a QPlainTextEdit object
        self.editor.setFont(fixedfont)
        self.editor.textChanged.connect(self.line_widget_line_count_changed)
        
        self.highlighter = Highlighter()
        self.highlighter.setDocument(self.editor.document())

        self.line_widget = LineNumberWidget(self.editor)
        # editor_layout = QHBoxLayout()
        # editor_layout.addWidget(self.line_widget)
        # editor_layout.addWidget(self.editor)
        
        # Call editor
        self.call_editor = QPlainTextEdit()
        self.call_editor.setFont(fixedfont)
        self.call_highlighter = Highlighter()
        self.call_highlighter.setDocument(self.call_editor.document())

        # Window for run result
        self.run_result = QPlainTextEdit(self)
        self.run_result.setFont(fixedfont)
        self.run_result.setReadOnly(True)
        
        # Right vertical spliter
        splitter1 = QSplitter(Qt.Orientation.Vertical)
        splitter1.addWidget(self.call_editor)
        splitter1.addWidget(self.run_result)

        # Main horizontal spliter
        splitter2 = QSplitter(Qt.Orientation.Horizontal)
        splitter2.addWidget(self.editor)
        splitter2.addWidget(splitter1)
        splitter2.setSizes([200, 100])

        layout.addWidget(self.line_widget)
        layout.addWidget(splitter2)                        # adding editor to the layout


        # Set central widget
        container = QWidget()              # creating a QWidget layout
        container.setLayout(layout)        # setting layout to the container
        self.setCentralWidget(container)   # making container as central widget

        # Status bar
        self.status = QStatusBar()         # creating a status bar object
        self.setStatusBar(self.status)     # setting stats bar to the window

        # Update statusbar when file is changed
        self.editor.textChanged.connect(self.update_statusbar)
        self.call_editor.textChanged.connect(self.update_statusbar)
        
        
        # ====== Menu bar ======
        menu_bar = self.menuBar()
        
        # === File menu in menu bar ===
        file_menu = menu_bar.addMenu("&File")               # creating a file menu
        
        # open file action
        open_file_action = QAction("Open file", self)       # creating a open file action
        open_file_action.setStatusTip("Open file")          # setting status tip
        open_file_action.triggered.connect(self.file_open)  # adding action to the open file
        open_file_action.setShortcut("Ctrl+O")              # setting shortcut
        file_menu.addAction(open_file_action)               # adding this to file menu

        # save action
        save_file_action = QAction("Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        save_file_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_file_action)

        # save as action
        saveas_file_action = QAction("Save As", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        saveas_file_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(saveas_file_action)


        # File tool bar
        # file_toolbar = QToolBar("File")                # creating a file tool bar
        # self.addToolBar(file_toolbar)                  # adding file tool bar to the window
        # file_toolbar.addAction(open_file_action)       # adding actions to tool bar
        # file_toolbar.addAction(save_file_action)
        # file_toolbar.addAction(saveas_file_action)
        # file_toolbar.addAction(print_action)

        # === Edit menu in menu bar ===
        edit_menu = self.menuBar().addMenu("&Edit")       # creating a edit menu bar

        # adding actions to the tool bar and menu bar
        undo_action = QAction("Undo", self)               # undo action
        undo_action.setStatusTip("Undo last change")      # adding status tip
        undo_action.triggered.connect(self.editor.undo)   # when triggered undo the editor
        edit_menu.addAction(undo_action)

        # redo action
        redo_action = QAction("Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        # cut action
        cut_action = QAction("Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        # copy action
        copy_action = QAction("Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        # paste action
        paste_action = QAction("Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        # select all action
        select_action = QAction("Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        # edit_toolbar = QToolBar("Edit")
        # self.addToolBar(edit_toolbar)# adding this tool bar to the main window
        # edit_toolbar.addAction(undo_action)# adding this to tool and menu bar
        # edit_toolbar.addAction(redo_action)
        # edit_toolbar.addAction(cut_action)
        # edit_toolbar.addAction(copy_action)
        # edit_toolbar.addAction(paste_action)
        # edit_toolbar.addAction(select_action)

        # wrap action
        wrap_action = QAction("Wrap text to window", self)
        wrap_action.setStatusTip("Check to wrap text to window")
        wrap_action.setCheckable(True)                        # making it checkable
        wrap_action.setChecked(True)                          # making it checked
        wrap_action.triggered.connect(self.edit_toggle_wrap)  # adding action
        edit_menu.addAction(wrap_action)                      # adding it to edit menu not to the tool bar
        
        # === Run menu in menu bar ===
        run_menu = self.menuBar().addMenu("&Run")

        run_action = QAction("Run", self)
        run_action.setStatusTip("Run program")
        run_action.triggered.connect(self.run_program)
        run_action.setShortcut("F5")
        run_menu.addAction(run_action)

        # === Debug menu in menu bar ===
        debug_menu = self.menuBar().addMenu("&Debug")

        mark_action = QAction("Mark", self)
        mark_action.setStatusTip("Mark functions for debug")
        mark_action.triggered.connect(self.mark_debug_func)
        mark_action.setShortcut("F7")
        debug_menu.addAction(mark_action)

        debug_action = QAction("Run and debug", self)
        debug_action.setStatusTip("Run and debug program")
        debug_action.triggered.connect(self.debug_program)
        debug_action.setShortcut("F8")
        debug_menu.addAction(debug_action)

        # === Run toolbar ===
        run_toolbar = QToolBar("Edit")
        self.addToolBar(run_toolbar)
        run_toolbar.addAction(run_action)
        

        self.update_statusbar()             # calling update title method
        self.show()                     # showing all the components

    def closeEvent(self, event):
        if not self.is_saved():
            self.unsaved_file_dialog()

    
    # creating dialog critical method
    # to show errors
    def dialog_critical(self, s):
        dlg = QMessageBox(self)            # creating a QMessageBox object
        dlg.setText(s)                     # setting text to the dlg
        dlg.setIcon(QMessageBox.Critical)  # setting icon to it
        dlg.show()                         # showing it

    
    def unsaved_file_dialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("File is unsaved")
        dlg.setText("Do you want to save changes?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()
        if button == QMessageBox.Yes:
            self.file_save()

    
    def line_widget_line_count_changed(self):
        # Signal for line widget
        if self.line_widget:
            n = int(self.editor.document().lineCount())
            self.line_widget.changeLineCount(n)

    
    def get_all_file_text(self):
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        text = definition + call
        return text

    
    def get_definition_text(self):
        return self.editor.toPlainText()

    
    def get_call_text(self):
        return self.call_editor.toPlainText()


    def is_saved(self):
        cur_text = self.get_all_file_text()
        return cur_text == self.saved_text

    
    def file_open(self):
        if not self.is_saved():
            self.unsaved_file_dialog()
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", 
                            "All files (*.*)")
        if path:
            try:
                with open(path) as f:
                    text = f.read()
            except Exception as e:
                self.dialog_critical(str(e))
            else:
                try:
                    definition, call = core.parse_code(text)
                except core.CodeFormatError:
                    definition, call = text, ""
                self.path = path
                self.editor.setPlainText(definition)
                self.call_editor.setPlainText(call)
                self.saved_text = self.get_all_file_text()
                self.update_statusbar()

    
    def file_save(self):
        if self.path is None:
            self.file_saveas()
            return
        self._save_to_path(self.path)

    
    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", 
                            "All files (*.*)")
        if not path:
            # return this method
            # i.e no action performed
            return
        self._save_to_path(path)

    
    def _save_to_path(self, path):
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        text = definition + call
        try:
            with open(path, 'w') as f:
                f.write(text)
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.path = path
            self.saved_text = self.get_all_file_text()
            self.update_statusbar()

    
    def update_statusbar(self):
        # setting window title with prefix as file name
        # suffix as PySide6 Notepad
        filename = self.path if self.path else "Untitled"
        is_saved_marker = "*" if not self.is_saved() else ""
        self.status.showMessage(f"File: {filename}{is_saved_marker}")

    
    # action called by edit toggle
    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    
    def run_program(self):
        if self.path is not None:
            self.file_save()
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        self.run_result.setPlainText("")
        try:
            func_dict = core.parse_def(definition)
            called_func = core.parse_call(call, func_dict)
        except Exception as e:
            self.run_result.setPlainText(str(e))
            return
        
        for func, args in called_func:
            try:
                ans = str(func(*args))
            except Exception as e:
                self.run_result.appendPlainText(str(e))
                return
            self.run_result.appendPlainText(ans)


    def mark_debug_func(self):
        # Try to parce definition
        definition = self.editor.toPlainText()
        try:
            func_dict = core.parse_def(definition)
        except Exception as e:
            self.dialog_critical("Error in the program. Debugging is not possible.")
            return
        # Exec dialog for marking debug func
        dlg = MarkDebugDialog(self, list(func_dict.keys()))
        if dlg.exec():
            # MarkDebugDialog return 'OK'
            self.debug_func_names = [checkbox.text() for checkbox in dlg.checkboxes if checkbox.isChecked()]
        else:
            # MarkDebugDialog return 'Cancel'
            pass


    def debug_program(self):
        if self.path is not None:
            self.file_save()
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        self.run_result.setPlainText("")
        try:
            func_dict = core.parse_def(definition)
        except Exception as e:
            self.run_result.setPlainText(str(e))
            return

        if not all([func_name in func_dict for func_name in self.debug_func_names]):
            self.mark_debug_func()

        for func_name in self.debug_func_names:
            func_dict[func_name].show_call = True

        try:
            called_func = core.parse_call(call, func_dict)
        except Exception as e:
            self.run_result.setPlainText(str(e))
            return
        
        for func, args in called_func:
            try:
                ans = str(func(*args))
            except Exception as e:
                self.run_result.appendPlainText(str(e))
                return
            self.run_result.appendPlainText(ans)
            self.run_result.appendPlainText(core.GLOBAL_DEBUG_LOG)
            core.GLOBAL_DEBUG_LOG = ""
        # TODO
        pass


def run_gui():
    app = QApplication(sys.argv)            # creating PySide6 application
    app.setApplicationName("GRF emulator")  # setting application name
    app.setStyleSheet(darkorange.getStyleSheet())
    window = MainWindow()                   # creating a main window object
    sys.exit(app.exec_())                   # loop
