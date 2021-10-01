# -*- coding: utf-8 -*-
# rename/app.py

"""This module provides the Rename File Tool application."""

import sys
from PyQt5.QtWidgets import QApplication
from .views import Window


def main():
    # Create the application
    app = QApplication(sys.argv)
    # Create and display the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())