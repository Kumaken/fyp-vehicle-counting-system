
from GUI.strings.params_input import DETECTION_INTERVAL_LABEL, DI_DEFAULT, MCDF_DEFAULT, MCDF_LABEL, MCTF_DEFAULT, MCTF_LABEL
from PyQt5.QtWidgets import ( QGridLayout, QLabel, QLineEdit )
from PyQt5.QtGui import QIntValidator

class ParamsInput:
    def __init__(self, parent=None):
        self.parent = parent
        self.layout = QGridLayout()
        self.di = None
        self.mcdf = None
        self.mctf = None

    def getLayout(self):
        return self.layout

    def update(self):
        self.di.setText(str(self.parent.getDI()))
        self.mctf.setText(str(self.parent.getMCTF()))
        self.mcdf.setText(str(self.parent.getMCDF()))

    def updateParent(self):
        self.parent.setDI(self.di)
        self.parent.setMCTF(self.mctf)
        self.parent.setMCDF(self.mcdf)

    def getParams(self):
        return dict(DETECTION_INTERVAL=int(self.di.text()), MCTF=int(self.mctf.text()), MCDF=int(self.mcdf.text()))

    def setup(self):
        # Detection Interval
        self.di = QLineEdit(DI_DEFAULT)
        self.di.setValidator(QIntValidator())
        self.layout.addWidget(QLabel(DETECTION_INTERVAL_LABEL), 0, 0)
        self.layout.addWidget(self.di, 1, 0)

        # MCTF
        self.mctf = QLineEdit(MCTF_DEFAULT)
        self.mctf.setValidator(QIntValidator())
        self.layout.addWidget(QLabel(MCTF_LABEL), 0, 1)
        self.layout.addWidget(self.mctf, 1, 1)

        # MCDF
        self.mcdf = QLineEdit(MCDF_DEFAULT)
        self.mcdf.setValidator(QIntValidator())
        self.layout.addWidget(QLabel(MCDF_LABEL), 0, 2)
        self.layout.addWidget(self.mcdf, 1, 2)

        return self