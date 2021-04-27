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
from GUI.sliders import Sliders
from GUI.gui_utils import GUIUtils
from GUI.custom_dict import CustomDict
from GUI.const import BUTTON_OPEN_IMG, BUTTON_SAVE_IMG, BUTTON_CAPTURE_IMG, SOURCE_IMG_PATH,IMAGE_DICT_KEYS, OUTPUT_IMG_QT
from GUI.video_player import VideoPlayer

class DisplayImageWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.sliders = []
        self.lines = []
        self.images_dict = CustomDict()
        for key in IMAGE_DICT_KEYS:
            self.images_dict[key] = None
        self.images_dict["qt_image_size"] = None
        self.images_dict["image_ratio"] = None

        self.label_dict = CustomDict({
            'image_label': QLabel(self),
            'mask_label' : QLabel(self),
            'mask_enhanced_label' : QLabel(self),
            'output_image_label' : QLabel(self),
            'text_label' : QLabel(self)
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
        GUIUtils.createHSVSliders(self.layout_dict.sliders_layout, self.sliders, self.images_dict, self.label_dict, self)
        second_column.addLayout(self.layout_dict.sliders_layout)

        buttons_layout = GUIUtils.setupButtons(self, self.buttons_dict, self.images_dict, self.label_dict, self.sliders)
        second_column.addLayout(buttons_layout)

        self.main_layout.addLayout(second_column)


        third_column = QGridLayout()
        GUIUtils.setupLineList(self, self.lines, third_column)
        self.main_layout.addLayout(third_column)



        GUIUtils.setupSourceImage(self.images_dict, self.label_dict)
        # Find the pixels that correspond to road
        # set lower and upper bounds
        GUIUtils.updateHSVMasking(self.images_dict, self.label_dict, self.sliders)


def start_GUI():
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    app.exec_()
    sys.exit(app.exec_())