from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QSlider, QGroupBox, QWidget)

class Sliders(QWidget):

    def __init__(self, name, slider_val=90, parent=None):
        super().__init__(parent=parent) # HAS TO PASS PARENT SO THIS COULD GET UPDATED (valueChanged called)
        vbox = QVBoxLayout()


        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(1)
        self.sl.setMaximum(255)
        self.sl.setValue(slider_val)
        self.sl.setFocusPolicy(Qt.StrongFocus)
        self.sl.setTickPosition(QSlider.TicksBothSides)
        self.sl.setTickInterval(1)
        self.sl.valueChanged[int].connect(self.valuechange)
        self.sl.resize(1000, self.height())

        vbox.addWidget(self.sl)

        self.l1 = QLabel("Value: " + str(self.sl.value()))
        self.l1.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.l1)

        # vbox.addStretch(1)
        # vbox.resize(1000, self.height())

        self.groupBox = QGroupBox(name)
        self.groupBox.setLayout(vbox)
        self.resize(1000, self.height())

    def valuechange(self, value):
        #self.size = self.sl.value()
        # self.__init__(value)
        print("value changes detected")
        self.l1.setText("Value: " + str(self.sl.value()));
        #return self.size

    def getComponent(self):
        return self.groupBox

    def getSliderValue(self):
        return self.sl.value();

    def setSliderValue(self, val):
        self.sl.setValue(val)

