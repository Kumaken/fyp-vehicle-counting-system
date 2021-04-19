from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider, QFileDialog, QLabel)

import cv2
import numpy as np
import sys

# import custom modules:
from sliders import Sliders
from gui_utils import GUIUtils
from custom_dict import CustomDict
from const import BUTTON_OPEN_IMG, BUTTON_SAVE_IMG, BUTTON_CAPTURE_IMG, SOURCE_IMG_PATH,IMAGE_DICT_KEYS
from video_player import VideoPlayer

class DisplayImageWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.sliders = []
        self.images_dict = CustomDict()
        for key in IMAGE_DICT_KEYS:
            self.images_dict[key] = None

        self.label_dict = CustomDict({
            'image_label': QLabel(self),
            'mask_label' : QLabel(self),
            'mask_enhanced_label' : QLabel(self),
            'output_image_label' : QLabel(self),
            'text_label' : QLabel(self)
        })
        self.main_layout = QVBoxLayout()
        self.layout_dict = CustomDict({
            'image_layout' : QGridLayout(),
            'sliders_layout' : QGridLayout()
        })
        self.buttons_dict = CustomDict({
            BUTTON_OPEN_IMG: None,
            BUTTON_SAVE_IMG: None,
            BUTTON_CAPTURE_IMG: None
        })

        # SET
        self.setup_GUI()

        # insert all the labels and layouts first before setLayout
        self.setLayout(self.main_layout)


    def setup_GUI(self):
        self.setWindowTitle("Qt static label demo")

        # create a vertical box layout and add the two labels
        self.main_layout = QVBoxLayout()
        GUIUtils.setupImageLayout(self.layout_dict.image_layout, self.label_dict)
        GUIUtils.setupButtons(self, self.buttons_dict, self.images_dict, self.label_dict, self.sliders, self.layout_dict.image_layout)
        self.main_layout.addLayout(self.layout_dict.image_layout)
        # set the vbox layout as the widgets layout
        self.setLayout(self.main_layout)

        # load the test image - we really should have checked that this worked!
        # self.images_dict.source_img_cv2 = cv2.imread(self.images_dict.SOURCE_IMG_PATH)
        # self.images_dict.source_img_cv2 = cv2.imread('data/images/road-no-cars.jpg')

        # SLIDERS:
        self.layout_dict.sliders_layout = QGridLayout()
        GUIUtils.createHSVSliders(self.layout_dict.sliders_layout, self.sliders, self.images_dict, self.label_dict, self)
        self.main_layout.addLayout(self.layout_dict.sliders_layout)


        GUIUtils.setupSourceImage(self.images_dict, self.label_dict)
        # Find the pixels that correspond to road
        # set lower and upper bounds
        GUIUtils.updateHSVMasking(self.images_dict, self.label_dict, self.sliders)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    sys.exit(app.exec_())