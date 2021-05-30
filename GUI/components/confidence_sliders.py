
from GUI.strings.confidence_sliders import NMS_THRESHOLD_LABEL, YOLO_CONFIDENCE_THRESHOLD_LABEL

from GUI.components.sliders import Sliders
from PyQt5.QtWidgets import ( QVBoxLayout)

class ConfidenceSliders:
    def __init__(self, parent=None):
        self.parent = parent
        self.layout = QVBoxLayout()
        self.yolo_conf_slider = None
        self.nms_slider = None

    def getLayout(self):
        return self.layout

    def update(self):
        self.yolo_conf_slider.setSliderValue(self.parent.getYoloConfidenceThreshold())
        self.nms_slider.setSliderValue(self.parent.getNMSThreshold())

    def setup(self):
        self.yolo_conf_slider = Sliders(YOLO_CONFIDENCE_THRESHOLD_LABEL, 20, 0.01, self.parent).setSliderRange(0, 100, 1).setConnect(self.parent.setYoloConfidenceThreshold) # IMPORTANT: PASS SELF AS PARENT!
        self.layout.addWidget(self.yolo_conf_slider.getComponent())


        self.nms_slider = Sliders(NMS_THRESHOLD_LABEL, 40, 0.01, self.parent).setSliderRange(0, 100, 1).setConnect(self.parent.setNMSThreshold)
        self.layout.addWidget(self.nms_slider.getComponent())
        return self