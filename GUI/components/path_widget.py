from PyQt5.QtWidgets import (QLabel, QPushButton, QGridLayout)
from GUI.strings.path_widget import CFG_PATH_PLACEHOLDER_STRING, IMAGE_PATH_STRING, IMAGE_PATH_PLACEHOLDER_STRING, LOAD_CFG_BUTTON_STRING, LOAD_CFG_BUTTON_TOOLTIP_STRING, WEIGHT_PATH_PLACEHOLDER_STRING, WEIGHT_PATH_STRING, CFG_PATH_STRING, VIDEO_PATH_PLACEHOLDER_STRING, VIDEO_PATH_STRING, LOAD_VIDEO_BUTTON_STRING, LOAD_VIDEO_BUTTON_TOOLTIP_STRING, LOAD_WEIGHT_BUTTON_STRING, LOAD_WEIGHT_BUTTON_TOOLTIP_STRING

from GUI.const import IMAGE_PATH_LABEL, VIDEO_PATH_LABEL, WEIGHT_PATH_LABEL, CFG_PATH_LABEL
from GUI.gui_utils import GUIUtils

class PathWidget:
    def __init__(self, parent=None):
        self.parent = parent
        self.path_layout = None
        self.image_path_label = None
        self.video_path_label = None
        self.weight_path_label = None
        self.cfg_path_label = None

        self.button_load_video = None
        self.button_load_weight = None

    def getLayout(self):
        return self.path_layout

    def loadWeight(self):
        filename = GUIUtils.selectFileDialog(self.parent, "Select a YOLOv4 weight", "Weights Files(*.weights)")
        self.parent.setWeight(filename)
        self.refreshLabels()

    def loadCFG(self):
        filename = GUIUtils.selectFileDialog(self.parent, "Select a YOLOv4 .cfg file", "CFG Files(*.cfg)")
        self.parent.setCFG(filename)
        self.refreshLabels()

    def refreshLabels(self):
        self.image_path_label.setText(self.parent.getSourceImagePath() or IMAGE_PATH_PLACEHOLDER_STRING)
        self.video_path_label.setText(self.parent.getVideoPath() or VIDEO_PATH_PLACEHOLDER_STRING)
        self.weight_path_label.setText(self.parent.getWeightPath() or WEIGHT_PATH_PLACEHOLDER_STRING)
        self.cfg_path_label.setText(self.parent.getCFGPath() or CFG_PATH_PLACEHOLDER_STRING)

    def setup(self ):
        self.path_layout = QGridLayout()
        self.path_layout.addWidget(QLabel(IMAGE_PATH_STRING), 0, 0)

        self.image_path_label = QLabel("")
        self.parent.getLabelDict()[IMAGE_PATH_LABEL] = self.image_path_label
        self.path_layout.addWidget(self.image_path_label, 1, 0)

        # VIDEO:
        self.button_load_video = GUIUtils.createButton(self.parent, LOAD_VIDEO_BUTTON_STRING, LOAD_VIDEO_BUTTON_TOOLTIP_STRING, lambda: GUIUtils.loadVideo(self.parent))
        self.path_layout.addWidget(self.button_load_video, 2, 1)

        self.path_layout.addWidget(QLabel(VIDEO_PATH_STRING), 2, 0)
        self.video_path_label = QLabel("")
        self.parent.getLabelDict()[VIDEO_PATH_LABEL] = self.video_path_label
        self.path_layout.addWidget(self.video_path_label, 3, 0)

        # Weights
        self.button_load_weight = GUIUtils.createButton(self.parent, LOAD_WEIGHT_BUTTON_STRING, LOAD_WEIGHT_BUTTON_TOOLTIP_STRING, self.loadWeight)
        self.path_layout.addWidget(self.button_load_weight, 4, 1)

        self.path_layout.addWidget(QLabel(WEIGHT_PATH_STRING), 4, 0)
        self.weight_path_label = QLabel("")
        self.parent.getLabelDict()[WEIGHT_PATH_LABEL] = self.weight_path_label
        self.path_layout.addWidget(self.weight_path_label, 5, 0)


        # CFG
        self.button_load_cfg = GUIUtils.createButton(self.parent, LOAD_CFG_BUTTON_STRING, LOAD_CFG_BUTTON_TOOLTIP_STRING, self.loadCFG)
        self.path_layout.addWidget(self.button_load_cfg, 6, 1)

        self.path_layout.addWidget(QLabel(CFG_PATH_STRING), 6, 0)
        self.cfg_path_label = QLabel("")
        self.parent.getLabelDict()[CFG_PATH_LABEL] = self.cfg_path_label
        self.path_layout.addWidget(self.cfg_path_label, 7, 0)

        # REFRESH
        self.refreshLabels()
        return self