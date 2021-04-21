from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QLabel)

class DetectorGUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Detector Controls")
        self.main_layout = QVBoxLayout()
        self.button_layout = QGridLayout()
        self.setupButtons()
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def setupButtons(self):
        from main import play_or_pause, screenshoot, stop
        start_btn = QPushButton('Start/Pause', self.parent)
        start_btn.setToolTip('Play or pause the detection process.')
        start_btn.clicked.connect(play_or_pause)
        self.button_layout.addWidget(start_btn, 0, 0)

        ss_btn = QPushButton('Screenshoot', self.parent)
        ss_btn.setToolTip('Take a screenshot of current frame.')
        ss_btn.clicked.connect(screenshoot)
        self.button_layout.addWidget(ss_btn, 0, 1)

        quit_btn = QPushButton('Exit', self.parent)
        quit_btn.setToolTip('Close the detection module.')
        quit_btn.clicked.connect(stop)
        self.button_layout.addWidget(quit_btn, 0, 2)