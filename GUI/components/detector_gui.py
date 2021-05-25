from GUI.strings.detector_gui import DETECTION_TABLE_COLUMN_HEADERS, FPS_STRING
from PyQt5 import  QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import ( QGridLayout, QPushButton, QTableWidgetItem, QVBoxLayout,QHeaderView, QLabel, QTableWidget)

class DetectorGUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Detector Controls")
        self.main_layout = QVBoxLayout()
        self.button_layout = QGridLayout()
        self.fps_label = None
        self.detection_table_layout = None
        self.detection_dict = {}

    def setup(self):
        self.setupFPS()
        self.setupDetectionTable()
        self.setupButtons()

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        return self

    def setupFPS(self):
        self.fps_label = QLabel(FPS_STRING+"0")
        self.main_layout.addWidget(self.fps_label)

    def refreshFPS(self, fps):
        self.fps_label.setText(FPS_STRING+fps)

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

    def setupDetectionTable(self):
        self.detection_table_layout = QVBoxLayout()
        self.main_layout.addLayout(self.detection_table_layout)

    def createDetectionTable(self, rowNum=2):
        detection_table = QTableWidget()
        detection_table.setRowCount(rowNum)
        detection_table.setColumnCount(2)
        detection_table.setHorizontalHeaderLabels(DETECTION_TABLE_COLUMN_HEADERS)

        # set table to fit window horizontally
        detection_table.horizontalHeader().setStretchLastSection(True)
        detection_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        return detection_table

    def refreshDetectionTable(self, detection):
        for line, objects in detection:
            if line not in self.detection_dict:
                self.detection_table_layout.addWidget(QLabel(line))
                table_widget = self.createDetectionTable(len(objects))
                self.detection_table_layout.addWidget(table_widget)
            else:
                table_widget = self.detection_dict[line]

            row = 0
            col = 0
            for label, count in objects.items():
                table_widget.setItem(row, col, QTableWidgetItem(label))
                table_widget.setItem(row, col+1, QTableWidgetItem(str(count)))
                row += 1

            self.detection_dict[line] = table_widget
