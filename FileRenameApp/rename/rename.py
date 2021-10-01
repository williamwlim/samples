# -*- coding: utf-8 -*-
# rename/rename.py

"""This module provides the Renamer class to rename multiple files."""

from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
import time


class Renamer(QObject):
    # Defining custom signals
    progressed = pyqtSignal(int)
    renamedFile = pyqtSignal(Path)
    finished = pyqtSignal()

    # Defining class constructor
    def __init__(self, files, prefix):
        super().__init__()
        self._files = files
        self._prefix = prefix

    def renameFiles(self):
        for fileNumber, file in enumerate(self._files, 1):
            newFile = file.parent.joinpath(
                f"{self._prefix}{str(fileNumber)}{file.suffix}"
            )
            file.rename(newFile)
            time.sleep(0.1)  # adding sleep time to check status bar display
            self.progressed.emit(fileNumber)
            self.renamedFile.emit(newFile)
        self.progressed.emit(0)  # Reset the progress bar
        self.finished.emit()