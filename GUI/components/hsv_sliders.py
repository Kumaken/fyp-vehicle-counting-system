
from GUI.strings.hsv_sliders import AUTO_MASKING_BUTTON, AUTO_MASKING_BUTTON_TOOLTIP
from GUI.components.sliders import Sliders
from GUI.gui_utils import GUIUtils
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout, QHBoxLayout, QVBoxLayout)
from GUI.const import SLIDER_LABELS

class HSVSliders:
    def __init__(self, parent=None):
        self.parent = parent
        self.layout = QVBoxLayout()
        self.auto_mask = [0,5,0,35,50,255]

    def getLayout(self):
        return self.layout


    def setAutoMasking(self):
        sliders = self.parent.getSliders()
        for i in range(len(self.auto_mask)):
            sliders[i].setSliderValue(self.auto_mask[i])

        GUIUtils.refreshImage(self.parent, self.parent.getImagesDict(), self.parent.getLabelDict(), sliders)


    def setup(self):
        self.layout = QVBoxLayout()

        button = QPushButton(AUTO_MASKING_BUTTON, self.parent)
        button.setToolTip(AUTO_MASKING_BUTTON_TOOLTIP)
        button.clicked.connect(self.setAutoMasking)
        self.layout.addWidget(button)

        grid = QGridLayout()
        sliders = self.parent.getSliders()
        for i in range(6):
            slider = Sliders(SLIDER_LABELS[i], 1 if i<3 else 255, parent=self.parent) # IMPORTANT: PASS SELF AS PARENT!
            slider.sl.valueChanged.connect(lambda: GUIUtils.refreshImage(self.parent, self.parent.getImagesDict(), self.parent.getLabelDict(), self.parent.getSliders()))

            sliders.append(slider)
            grid.addWidget(slider.getComponent(), i % 3, 0 if i < 3 else 1)

        self.layout.addLayout(grid)
        return self