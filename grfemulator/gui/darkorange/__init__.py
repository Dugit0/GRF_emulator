from . import darkorange
from PySide6 import QtCore
from pathlib import Path
import sys

def getStyleSheet():
    path = Path(__file__).resolve().parent / "darkorange.qss"
    with open(path) as f:
        return f.read()
