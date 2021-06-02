from GUI.components.params_input import ParamsInput
from GUI.components.confidence_sliders import ConfidenceSliders
from GUI.components.hsv_sliders import HSVSliders
from GUI.components.counting_mode_radio_button import CountingModeRadioButton
from GUI.components.tracker_selector import TrackerSelector
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QHBoxLayout,
                             QVBoxLayout, QWidget, QSlider, QFileDialog, QLabel)
from PyQt5.QtGui import QPainter, QPen

import cv2
import numpy as np
import sys

# import custom modules:
from GUI.gui_utils import GUIUtils
from GUI.custom_dict import CustomDict
from GUI.const import BUTTON_OPEN_IMG, BUTTON_SAVE_IMG, BUTTON_CAPTURE_IMG, SOURCE_IMG_PATH,IMAGE_DICT_KEYS, OUTPUT_IMG_QT, PLACEHOLDER_IMG_PATH
from GUI.video_player import VideoPlayer

from GUI.components.path_widget import PathWidget
class DisplayImageWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.sliders = []
        self.lines = []
        self.highlighted_line = None
        self.images_dict = CustomDict()
        for key in IMAGE_DICT_KEYS:
            self.images_dict[key] = None
        self.images_dict["qt_image_size"] = None
        self.images_dict["image_ratio"] = None
        self.video_path = None

        self.label_dict = CustomDict({
            'image_label': QLabel(self),
            'mask_label' : QLabel(self),
            'mask_enhanced_label' : QLabel(self),
            'output_image_label' : QLabel(self),
            'text_label' : QLabel(self),
            'image_path' : None,
            'video_path': None
        })
        self.main_layout = QHBoxLayout()
        self.layout_dict = CustomDict({
            'image_layout' : QGridLayout(),
            'sliders_layout' : QGridLayout()
        })
        self.buttons_dict = CustomDict({
            BUTTON_OPEN_IMG: None,
            BUTTON_SAVE_IMG: None,
            BUTTON_CAPTURE_IMG: None
        })
        self.line_list_widget = None
        self.weight_path = None
        self.cfg_path = None

        # trackers
        self.chosen_tracker = None
        self.tracker_selector = None

        # detection mode
        self.counting_mode = None

        # widgets
        self.path_widget = None

        # params
        self.di = None
        self.mctf = None
        self.mcdf = None

        # confidence thresholds:
        self.yolo_conf_threshold = 0.2
        self.nms_threshold = 0.4
        self.conf_sliders = None

        # SET
        self.setup_GUI()

        # insert all the labels and layouts first before setLayout
        self.setLayout(self.main_layout)

     # inherited callback when the window closes!
    def closeEvent(self, event):
        sys.exit() # force end program when this window is closed

    # # override
    # def paintEvent(self, event):
    #     pixmap = self.images_dict[OUTPUT_IMG_QT]
    #     if not pixmap:
    #         return
    #     painter = QPainter(self)
    #     painter.drawPixmap(self.rect(), pixmap)
    #     pen = QPen(Qt.red, 3)
    #     painter.setPen(pen)
    #     painter.drawLine(10, 10, self.rect().width() -10 , 10)
    #     self.images_dict[OUTPUT_IMG_QT] = pixmap

    def setup_GUI(self):
        self.setWindowTitle("HSV Based RoI Segmentations")

        # create a vertical box layout and add the two labels
        GUIUtils.setupImageLayout(self, self.layout_dict.image_layout, self.label_dict, self.images_dict)
        self.main_layout.addLayout(self.layout_dict.image_layout)

        # SLIDERS:
        self.layout_dict.sliders_layout = QGridLayout()
        second_column = QVBoxLayout()
        second_column.addLayout(HSVSliders(self).setup().getLayout())
        # GUIUtils.createHSVSliders(self.layout_dict.sliders_layout, self.sliders, self.images_dict, self.label_dict, self)
        # second_column.addLayout(self.layout_dict.sliders_layout)

        buttons_layout = GUIUtils.setupButtons(self, self.buttons_dict, self.images_dict, self.label_dict, self.sliders)
        second_column.addLayout(buttons_layout)

        self.main_layout.addLayout(second_column)


        third_column = QVBoxLayout()
        # line list widget
        list_layout = QGridLayout()
        GUIUtils.setupLineList(self, self.lines, list_layout)
        third_column.addLayout(list_layout)

        # detection mode radio button
        self.counting_mode_radio_button = CountingModeRadioButton(self).setup()
        third_column.addLayout(self.counting_mode_radio_button.getLayout())

        # tracker selector
        self.tracker_selector = TrackerSelector(self).setup()
        third_column.addLayout(self.tracker_selector.getLayout())

        # params input
        self.params_input = ParamsInput(self).setup()
        third_column.addLayout(self.params_input.getLayout())

        # confidence sliders
        self.conf_sliders = ConfidenceSliders(self).setup()
        third_column.addLayout(self.conf_sliders.getLayout())

        # paths widget
        self.path_widget = PathWidget(self)
        third_column.addLayout(self.path_widget.setup().getLayout())

        self.main_layout.addLayout(third_column)

        # setup placeholder image:
        self.images_dict[SOURCE_IMG_PATH] = PLACEHOLDER_IMG_PATH
        GUIUtils.setupSourceImage(self.images_dict, self.label_dict)
        GUIUtils.refreshImage(self, self.images_dict, self.label_dict, self.sliders)

    # setters
    def setWeight(self, weight_path):
        self.weight_path = weight_path

    def setCFG(self, cfg_path):
        self.cfg_path = cfg_path

    def setChosenTracker(self, tracker):
        self.chosen_tracker = tracker

    def setCountingMode(self, mode):
        self.counting_mode = mode

    def addSlider(self, slider):
        self.sliders.append(slider)

    def setHighlightedLine(self, line_name):
        self.highlighted_line = line_name

    def setYoloConfidenceThreshold(self, val):
        # print("VAL:", val)
        self.yolo_conf_threshold = float(val)

    def setNMSThreshold(self, val):
        self.nms_threshold = float(val)

    def setDI(self, val):
        self.di = val

    def setMCTF(self, val):
        self.mctf = val

    def setMCDF(self, val):
        self.mcdf = val

    # getters:
    def getSourceImagePath(self):
        return self.images_dict[SOURCE_IMG_PATH]

    def getVideoPath(self):
        return self.video_path

    def getWeightPath(self):
        return self.weight_path

    def getCFGPath(self):
        return self.cfg_path

    def getLabelDict(self):
        return self.label_dict

    def getPathWidget(self):
        return self.path_widget

    def getChosenTracker(self):
        return self.chosen_tracker

    def getTrackerSelector(self):
        return self.tracker_selector

    def getCountingMode(self):
        return self.counting_mode

    def getCountingModeRadioButton(self):
        return self.counting_mode_radio_button

    def getImagesDict(self):
        return self.images_dict

    def getLabelDict(self):
        return self.label_dict

    def getSliders(self):
        return self.sliders

    def getHighlightedLine(self):
        return self.highlighted_line

    def getYoloConfidenceThreshold(self):
        return self.yolo_conf_threshold

    def getNMSThreshold(self):
        return self.nms_threshold

    def getConfSliders(self):
        return self.conf_sliders

    def getDI(self):
        return int(self.di) if self.di else self.di

    def getMCTF(self):
        return int(self.mctf) if self.mctf else self.mctf

    def getMCDF(self):
        return int(self.mcdf) if self.mcdf else self.mcdf

    def getParamsInput(self):
        return self.params_input

def start_GUI():
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    app.exec_()
    sys.exit(app.exec_())