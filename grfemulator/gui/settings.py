from PySide6.QtCore import (QSize)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QWidget, QDialog, QDialogButtonBox,
                               QVBoxLayout, QHBoxLayout, QFormLayout,
                               QTabWidget, QLabel, QComboBox)

from .globalresources import LOGO_PATH, COLOR_SCHEMES_PATH

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
        self.schemes = [s.stem for s in COLOR_SCHEMES_PATH.iterdir()]
        self.color_combo_box.addItems(self.schemes)
        cur_text = parent.settings.value("COLOR_SCHEME", "aqua", type=str)
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
                str(self.color_combo_box.currentText())
                )
        if not self.apply_flag:
            self.apply_flag = True
            self.update_label.setText(self.update_message)
