from GUI.strings.counting_mode_radio_button import counting_mode_SELECTION_MESSAGE
from PyQt5.QtWidgets import (QLabel, QRadioButton, QVBoxLayout, QHBoxLayout)
from GUI.strings.counting_mode_radio_button import COUNTING_MODE_INCREMENTAL, COUNTING_MODE_ACTUAL

class CountingModeRadioButton:
    def __init__(self, parent=None):
        self.parent = parent
        self.counting_modes = [COUNTING_MODE_INCREMENTAL, COUNTING_MODE_ACTUAL]
        self.layout = QVBoxLayout()
        self.radio_button_group = []

    def createTrackerPrefixString(self, prefix, tracker):
        return "{0} {1}".format(prefix, tracker)

    def updateParent(self, mode):
        self.parent.setCountingMode(mode)

    def update(self, mode):
        print("[DEBUG] update mode", mode)
        for radio_button in self.radio_button_group:
            if radio_button.mode == mode:
                print("[DEBUG] Detection mode selected:", radio_button.mode)
                radio_button.setChecked(True)
                return

    def getLayout(self):
        return self.layout

    def onClicked(self, is_checked):
        if not is_checked:
            return
        for radio_button in self.radio_button_group:
            if radio_button.isChecked():
                print("[DEBUG] Detection mode selected:", radio_button.mode)
                self.updateParent(radio_button.mode)
                return


    def setup(self):
        msg_label = QLabel(counting_mode_SELECTION_MESSAGE)
        self.layout.addWidget(msg_label)

        radioButtonLayout = QHBoxLayout()
        for counting_mode in self.counting_modes:
            radioButton = QRadioButton(counting_mode)
            radioButton.mode = counting_mode
            radioButton.toggled.connect(lambda is_checked: self.onClicked(is_checked))
            radioButtonLayout.addWidget(radioButton)
            self.radio_button_group.append(radioButton)

        radioButton.setChecked(True)

        self.layout.addLayout(radioButtonLayout)

        return self