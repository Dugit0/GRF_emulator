from . import aqua
from PySide6 import QtCore
from pathlib import Path

def getStyleSheet():
    path = Path(__file__).resolve().parent / "aqua.qss"
    with open(path) as f:
        return f.read()
