import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class LineListWidget(QListWidget):
    def __init__(self, parent, lines):
        super(LineListWidget,self).__init__()
        self.parent = parent

    def clicked(self, item):
        QMessageBox.information(self, "ListWidget", "ListWidget: " + item.text())

    def setupList(self):
        print("Setup List!", self.parent.lines)
        self.clear()
        for line_entry in self.parent.lines:
            self.addItem(line_entry['label'])
        self.itemClicked.connect(self.clicked)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     listWidget = ListWidget()

#     listWidget.resize(300, 120)
#     listWidget.addItem("Item 1")
#     listWidget.addItem("Item 2")
#     listWidget.addItem("Item 3")
#     listWidget.addItem("Item 4")

#     listWidget.itemClicked.connect(listWidget.clicked)

#     listWidget.show()
#     sys.exit(app.exec_())