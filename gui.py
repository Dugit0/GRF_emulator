from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from LineNumberWidget import LineNumberWidget
import GRFCore
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



class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None
        
        self.defcall_splitter = "!!!"

        self.setGeometry(100, 100, 1000, 700)   # setting window geometry
        
        layout = QHBoxLayout()   # creating a layout

        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) # setting font to the editor
        fixedfont.setPointSize(12)
        
        # Main editor and line number widget
        self.editor = QPlainTextEdit()                                # creating a QPlainTextEdit object
        self.editor.setFont(fixedfont)
        self.editor.textChanged.connect(self.line_widget_line_count_changed)
        self.line_widget = LineNumberWidget(self.editor)
        # editor_layout = QHBoxLayout()
        # editor_layout.addWidget(self.line_widget)
        # editor_layout.addWidget(self.editor)
        
        # Call editor
        self.call_editor = QPlainTextEdit()
        self.call_editor.setFont(fixedfont)

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

        # === Run toolbar ===
        run_toolbar = QToolBar("Edit")
        self.addToolBar(run_toolbar)
        run_toolbar.addAction(run_action)
        

        self.update_title()             # calling update title method
        self.show()                     # showing all the components

    
    # creating dialog critical method
    # to show errors
    def dialog_critical(self, s):
        dlg = QMessageBox(self)            # creating a QMessageBox object
        dlg.setText(s)                     # setting text to the dlg
        dlg.setIcon(QMessageBox.Critical)  # setting icon to it
        dlg.show()                         # showing it

    def line_widget_line_count_changed(self):
        if self.line_widget:
            n = int(self.editor.document().lineCount())
            self.line_widget.changeLineCount(n)


    
    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", 
                            "All files (*.*)")
        if path:
            try:
                with open(path) as f:
                    text = f.read()
            except Exception as e:
                self.dialog_critical(str(e))
            else:
                definition, _, call = text.partition(self.defcall_splitter)
                self.path = path
                self.editor.setPlainText(definition)
                self.call_editor.setPlainText(call)
                self.update_title()

    
    def file_save(self):
        if self.path is None:
            return self.file_saveas()
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
        text = definition + self.defcall_splitter + call
        try:
            with open(path, 'w') as f:
                f.write(text)
        except Exception as e:
            self.dialog_critical(str(e))
        else:
            self.path = path
            self.update_title()

    
    def update_title(self):
        # setting window title with prefix as file name
        # suffix as PyQt5 Notepad
        filename = os.path.basename(self.path) if self.path else "Untitled"
        self.setWindowTitle(f"{filename} - GRF emulator")

    
    # action called by edit toggle
    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    
    def run_program(self):
        if self.path is not None:
            self.file_save()
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        GRFCore.parse_def(definition)
        called_func = GRFCore.parse_call(call)
        ans = [str(func(*args)) for func, args in called_func]
        self.run_result.setPlainText("\n".join(ans))




if __name__ == '__main__':
    app = QApplication(sys.argv)            # creating PyQt5 application
    app.setApplicationName("GRF emulator")  # setting application name
    window = MainWindow()                   # creating a main window object
    sys.exit(app.exec_())                   # loop

