# -*- coding: utf-8 -*-

"""This module provides the Rename File Tool main window."""
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QWidget
from .rename import Renamer
from rename.window import Ui_Window
from collections import deque
from pathlib import Path


FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.txt)",
    )
)


class Window(QWidget, Ui_Window):
    # class constructor
    def __init__(self):
        super().__init__()
        self.files = deque()
        self.filesCount = len(self.files)
        self.setupui()
        self.connectSignalsSlots()

    def setupui(self):
        self.setupUi(self)
        self.updateStateWhenNoFiles()

    def updateStateWhenNoFiles(self):
        self.filesCount = len(self.files)
        self.loadFilesButton.setEnabled(True)
        self.loadFilesButton.setFocus(True)
        self.renameFilesButton.setEnabled(False)
        self.prefixEdit.clear()
        self.prefixEdit.setEnabled(False)

    def connectSignalsSlots(self):
        self.loadFilesButton.clicked.connect(self.loadFiles)
        self.renameFilesButton.clicked.connect(self.renameFiles)
        self.prefixEdit.textChanged.connect(self.updateStateWhenReady)

    def updateStateWhenReady(self):
        if self.prefixEdit.text():
            self.renameFilesButton.setEnabled(True)
        else:
            self.renameFilesButton.setEnabled(False)

    def loadFiles(self):
        self.dstFileList.clear()
        if self.dirEdit.text():
            initDir = self.dirEdit.text()
        else:
            initDir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", initDir, filter=FILTERS
        )
        if len(files) > 0:
            fileExtension = filter[filter.index("*") : -1]
            self.extensionLabel.setText(fileExtension)
            srcDirName = str(Path(files[0]).parent)
            self.dirEdit.setText(srcDirName)
            for file in files:
                self.files.append(Path(file))
                self.srcFileList.addItem(file)
            self.filesCount = len(self.files)
            self.updateStateWhenFilesLoaded()

    def updateStateWhenFilesLoaded(self):
        self.prefixEdit.setEnabled(True)
        self.prefixEdit.setFocus(True)

    def renameFiles(self):
        self.runRenamerThread()
        self.updateStateWhileRenaming()

    def updateStateWhileRenaming(self):
        self.loadFilesButton.setEnabled(False)
        self.renameFilesButton.setEnabled(False)

    def runRenamerThread(self):
        prefix = self.prefixEdit.text()
        self.thread = QThread()
        self.renamer = Renamer(
            files=tuple(self.files),
            prefix=prefix,
        )
        self.renamer.moveToThread(self.thread)
        # Renaming Files
        self.thread.started.connect(self.renamer.renameFiles)
        # Updating state
        self.renamer.renamedFile.connect(self.updateStateWhenFileRenamed)
        self.renamer.progressed.connect(self.updateProgressBar)
        self.renamer.finished.connect(self.updateStateWhenNoFiles)
        # Clean up
        self.renamer.finished.connect(self.thread.quit)
        self.renamer.finished.connect(self.renamer.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Initiating thread
        self.thread.start()

    def updateStateWhenFileRenamed(self, newFile):
        self.files.popleft()
        self.srcFileList.takeItem(0)
        self.dstFileList.addItem(str(newFile))

    def updateProgressBar(self, fileNumber):
        progressPercent = int(fileNumber / self.filesCount * 100)
        self.progressBar.setValue(progressPercent)