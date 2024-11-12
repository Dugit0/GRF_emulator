from PySide6.QtGui import (QColor, QIcon, QAction, QFont, QFontDatabase,
                           QSyntaxHighlighter, QTextCharFormat, QTextDocument)
from PySide6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon,
                               QMainWindow, QDialog, QTextEdit,
                               QVBoxLayout, QHBoxLayout, QFormLayout,
                               QPlainTextEdit, QSplitter, QTabWidget,
                               QStatusBar, QToolBar, QComboBox, QLabel,
                               QCheckBox, QMessageBox, QFileDialog,
                               QDialogButtonBox)
from PySide6.QtCore import (Qt, QObject, Signal, Slot, QRunnable, QThreadPool,
                            QCoreApplication, QSize, QSettings)
from .LineNumberWidget import LineNumberWidget
from .. import __version__
from .. import core
from . import darkorange
import time
import traceback
import webbrowser
import re
from pathlib import Path
import sys

"""
TODO:
    QToolTip
    exitAction.setShortcut('Ctrl+Q')
"""

LOGO_PATH = str(Path(__file__).resolve().parent / "logo.png")
HELP_PATH = str(Path(__file__).resolve().parent / "help.html")
COLOR_SCHEMES_PATH = Path(__file__).resolve().parent / "schemes"


class WorkerSignals(QObject):
    """
    Определяет сигналы доступные в выполняющемся треде класса Worker.

    Поддерживаемые сигналы:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object результат выполнения функции треда
    """

    finished = Signal()  # QtCore.Signal
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    Обертка над тредом.

    Унаследован от QRunnable. Создает и присоединяет сигналы к треду.

    :param func: Функция запускающаяся в треде.
    :type func: function
    :param args: ``args`` передающиеся в ``func``
    :param progress_flag: следует выставить True, если у функции есть
    возможность посылать сигнал progress для обновления информации в GUI.
    По умолчанию False.
    """

    def __init__(self, func, *args, progress_flag=False):
        """Обертка над тредом."""
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.func = func
        self.args = args
        self.progress_flag = progress_flag
        self.signals = WorkerSignals()

    @Slot()  # QtCore.Slot
    def run(self):
        """Запускает функцию с параметрами ``args`` и ``kwargs``."""
        try:
            if self.progress_flag:
                result = self.func(*self.args,
                                   progress=self.signals.progress)
            else:
                result = self.func(*self.args)
        except Exception as e:
            # traceback.print_exc()
            # exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(str(e))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            # Done
            self.signals.finished.emit()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(LOGO_PATH))
        default_size = int(min(parent.width(), parent.height()) * 0.7)
        self.setMinimumSize(QSize(default_size, default_size))

        self.apply_flag = False
        self.update_message = "To apply the settings, restart the application!"

        layout = QVBoxLayout()
        tabs = QTabWidget()

        # View page
        view_page = QWidget(self)
        self.view_page_layout = QFormLayout()
        self.color_combo_box = QComboBox(self)
        self.schemes = {s.stem: s for s in COLOR_SCHEMES_PATH.glob("*.qss")}
        self.color_combo_box.addItems(list(self.schemes.keys()))
        cur_text = Path(
                parent.settings.value("COLOR_SCHEME",
                                      str(COLOR_SCHEMES_PATH / "Aqua.qss"),
                                      type=str)
                ).stem
        self.color_combo_box.setCurrentText(cur_text)
        self.update_label = QLabel(" " * len(self.update_message))

        self.view_page_layout.addRow("Color scheme:", self.color_combo_box)
        self.view_page_layout.addRow(self.update_label, QLabel())
        view_page.setLayout(self.view_page_layout)
        tabs.addTab(view_page, 'View settings')

        button_box = QDialogButtonBox()
        apply_button = button_box.addButton("Apply",
                                            QDialogButtonBox.ApplyRole)
        cancel_button = button_box.addButton("Cancel",
                                             QDialogButtonBox.RejectRole)
        apply_button.clicked.connect(self.accept_settings)
        # button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(tabs)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept_settings(self):
        self.parent().settings.setValue(
                "COLOR_SCHEME",
                str(self.schemes[self.color_combo_box.currentText()])
                )
        if not self.apply_flag:
            self.apply_flag = True
            self.update_label.setText(self.update_message)


class MarkDebugDialog(QDialog):
    def __init__(self, parent, func_names):
        super().__init__(parent)

        self.setWindowTitle("Functions for debugging")
        self.setWindowIcon(QIcon(LOGO_PATH))

        self.layout = QVBoxLayout()

        message = QLabel("Mark functions for debugging")
        self.layout.addWidget(message)

        self.checkboxes = [QCheckBox(name, self) for name in func_names]
        for checkbox in self.checkboxes:
            self.layout.addWidget(checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)
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
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None
        self.saved_text = ""
        self.debug_func_names = []
        self.run_counter = 1
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.semafor = False

        self.setWindowIcon(QIcon(LOGO_PATH))
        self.setWindowTitle("GRF emulator")
        self.setGeometry(100, 100, 1200, 700)   # setting window geometry

        self.settings = QSettings()
        color_scheme = self.settings.value(
                "COLOR_SCHEME",
                str(COLOR_SCHEMES_PATH / "Aqua.qss"),
                type=str
                )
        app = QCoreApplication.instance()
        with open(color_scheme) as color_scheme_file:
            app.setStyleSheet(color_scheme_file.read())

        layout = QHBoxLayout()

        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) # setting font to the editor
        fixedfont.setPointSize(12)

        # Main editor and line number widget
        self.editor = QPlainTextEdit()
        self.editor.setFont(fixedfont)
        self.editor.textChanged.connect(self.line_widget_line_count_changed)

        self.highlighter = Highlighter()
        self.highlighter.setDocument(self.editor.document())

        self.line_widget = LineNumberWidget(self.editor)

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
        layout.addWidget(splitter2)


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
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        # redo action
        redo_action = QAction("Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addAction(redo_action)

        # cut action
        cut_action = QAction("Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.editor.cut)
        cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(cut_action)

        # copy action
        copy_action = QAction("Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.editor.copy)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        # paste action
        paste_action = QAction("Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.triggered.connect(self.editor.paste)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        # select all action
        select_action = QAction("Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(self.editor.selectAll)
        select_action.setShortcut("Ctrl+A")
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
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

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

        # === Settings menu in menu bar ===
        settings_menu = self.menuBar().addMenu("&Settings")

        help_action = QAction("Help", self)
        help_action.setStatusTip("Help")
        help_action.triggered.connect(self.open_help_menu)
        help_action.setShortcut("F1")
        settings_menu.addAction(help_action)

        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Settings menu")
        settings_action.triggered.connect(self.open_settings_menu)
        settings_action.setShortcut("F4")
        settings_menu.addAction(settings_action)

        # DEBUG menu
        # TODO delete this function
        # === Test menu in menu bar ===
        # test_menu = self.menuBar().addMenu("&TEST")

        # test_action = QAction("Color schemes test", self)
        # test_action.setStatusTip("Color schemes test")
        # test_action.triggered.connect(self.color_schemes_test)
        # test_menu.addAction(test_action)

        # === Run toolbar ===
        run_toolbar = QToolBar("Edit")
        self.addToolBar(run_toolbar)
        run_toolbar.addAction(run_action)


        self.update_statusbar()         # calling update title method
        self.show()                     # showing all the components


    # DEBUG function
    # TODO delete this function
    # def color_schemes_test(self):
    #     for path in COLOR_SCHEMES_PATH.glob("*.qss"):
    #         app = QCoreApplication.instance()
    #         app.setStyleSheet(get_style_sheet(str(path)))
    #         time.sleep(5)


    def closeEvent(self, event):
        if not self.is_saved():
            self.unsaved_file_dialog()


    # creating dialog critical method to show errors
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
        if definition and call:
            # definition and call not empty
            text = definition + "\n\n" + call
        else:
            # for correct saving empty files
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
        text = self.get_all_file_text()
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
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0
                                    else 0)

    # def __exception_print(self, error):
    #     # error = (exctype, value, traceback.format_exc())
    #     self.run_result.appendPlainText(str(error[2]))

    def __run_program_in_thread(self):
        if self.path is not None:
            self.file_save()
        definition = self.editor.toPlainText()
        call = self.call_editor.toPlainText()
        self.run_result.setPlainText("")
        # TODO run counter
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

    def __set_semafor_false(self):
        self.semafor = False

    def run_program(self):
        worker = Worker(self.__run_program_in_thread)
        worker.signals.finished.connect(self.__set_semafor_false)
        # TODO Это костыль, чтобы нельзя было запустить больше одного процесса
        # Нужно это убрать и сделать возможность останавливать задачу
        if (self.semafor):
            return
        self.semafor = True
        self.threadpool.start(worker)


    def open_settings_menu(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            # MarkDebugDialog return 'OK'
            pass
        else:
            # MarkDebugDialog return 'Cancel'
            pass


    def open_help_menu(self):
        webbrowser.open(HELP_PATH)

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
            self.debug_func_names = [checkbox.text()
                                     for checkbox in dlg.checkboxes
                                     if checkbox.isChecked()]
        else:
            # MarkDebugDialog return 'Cancel'
            pass


    def __run_debug_in_thread(self):
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

        if not all([func_name in func_dict
                    for func_name in self.debug_func_names]):
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


    def debug_program(self):
        worker = Worker(self.__run_debug_in_thread)
        worker.signals.finished.connect(self.__set_semafor_false)
        # TODO Это костыль, чтобы нельзя было запустить больше одного процесса
        # Нужно это убрать и сделать возможность останавливать задачу
        if (self.semafor):
            return
        self.semafor = True
        self.threadpool.start(worker)



def run_gui():
    app = QApplication(sys.argv)            # creating PySide6 application
    app.setApplicationName("GRF emulator")  # setting application name
    app.setOrganizationName(app.applicationName())
    app.setOrganizationDomain("https://github.com/Dugit0/GRF_emulator")
    app.setApplicationVersion(__version__)
    window = MainWindow()                   # creating a main window object
    sys.exit(app.exec_())                   # loop
