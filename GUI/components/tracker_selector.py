from PyQt5.QtWidgets import (QLabel, QComboBox, QVBoxLayout)
from GUI.strings.tracker_options import CSRT, KCF, BOOSTING, MIL, NO_TRACKER, TLD, MEDIANFLOW, MOSSE, TRACKER_DEFAULT, TRACKER_PREFIX

class TrackerSelector:
    def __init__(self, parent=None):
        self.parent = parent
        self.tracker_options = [KCF, CSRT, BOOSTING, MIL, TLD, MEDIANFLOW, MOSSE, NO_TRACKER]
        self.chosen_tracker_label = QLabel(self.createTrackerPrefixString(TRACKER_PREFIX, TRACKER_DEFAULT))
        self.combo_box = QComboBox(self.parent)
        self.layout = QVBoxLayout()

    def createTrackerPrefixString(self, prefix, tracker):
        return "{0} {1}".format(prefix, tracker)

    def updateLabel(self):
        text = self.parent.getChosenTracker()
        formatted_text = self.createTrackerPrefixString(TRACKER_PREFIX, text)
        self.chosen_tracker_label.setText(formatted_text)
        self.chosen_tracker_label.adjustSize()
        self.combo_box.setCurrentText(text)

    def getLayout(self):
        return self.layout

    def onChanged(self, idx):
        text = self.tracker_options[idx]
        formatted_text = self.createTrackerPrefixString(TRACKER_PREFIX, text)
        self.chosen_tracker_label.setText(formatted_text)
        self.chosen_tracker_label.adjustSize()
        self.parent.setChosenTracker(text)

    def setup(self):
        for option in self.tracker_options:
            self.combo_box.addItem(option)

        self.combo_box.currentIndexChanged.connect(lambda idx: self.onChanged(idx))
        # set default tracker
        self.parent.setChosenTracker(TRACKER_DEFAULT)

        self.layout.addWidget(self.chosen_tracker_label)
        self.layout.addWidget(self.combo_box)

        return self