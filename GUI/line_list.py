import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QListWidget, QToolButton, QHBoxLayout, QWidget, QListWidgetItem, QMessageBox, QInputDialog, QLineEdit

class LineListWidget(QListWidget):
    def __init__(self, parent, lines):
        super(LineListWidget,self).__init__()
        self.parent = parent

    # def clicked(self, item):
    #     QMessageBox.information(self, "ListWidget", "ListWidget: " + item.text())

    def deleteItem(self, item):
        from GUI.gui_utils import GUIUtils
        print("Deleting line :", item.text())
        i = 0
        while i < len(self.parent.lines):
            if self.parent.lines[i]['label'] == item.text():
                del self.parent.lines[i]
                continue
            i += 1
        # delete from list:
        items_list = self.findItems(item.text(), Qt.MatchExactly)
        for item_ in items_list:
            r = self.row(item_)
            self.takeItem(r)
        # self.takeItem(self.row(item))
        print(self.parent.lines)
        result_cv2_img = GUIUtils.drawLines(self.parent, self.parent.images_dict)
        GUIUtils.applyLines(self.parent.label_dict, result_cv2_img)

    def renameItem(self, item):
        new_label, ok_pressed = QInputDialog.getText(self, "Select new label for this line","New label:", QLineEdit.Normal, item.text())

        if ok_pressed and new_label != '':
            i = 0
            while i < len(self.parent.lines):
                if self.parent.lines[i]['label'] == item.text():
                    self.parent.lines[i]['label'] = new_label
                i += 1

            items_list = self.findItems(item.text(), Qt.MatchExactly)
            for item_ in items_list:
                item_.setText(new_label)
            print(self.parent.lines)
            from GUI.gui_utils import GUIUtils
            result_cv2_img = GUIUtils.drawLines(self.parent, self.parent.images_dict)
            GUIUtils.applyLines(self.parent.label_dict, result_cv2_img)


    def createLineEntry(self, label):
        item = QListWidgetItem(label)
        self.addItem(item)
        widget = QWidget(self)

        del_button = QToolButton(widget)
        icon = QIcon()
        icon.addPixmap(QPixmap("GUI/icons/delete.png"), QIcon.Normal, QIcon.Off)
        del_button.setIcon(icon)
        del_button.clicked.connect(lambda: self.deleteItem(item))

        edit_button = QToolButton(widget)
        edit_icon = QIcon()
        edit_icon.addPixmap(QPixmap("GUI/icons/edit.png"), QIcon.Normal, QIcon.Off)
        edit_button.setIcon(edit_icon)
        edit_button.clicked.connect(lambda: self.renameItem(item))


        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(del_button)
        layout.addWidget(edit_button)
        self.setItemWidget(item, widget)




    def setupList(self):
        # print("Setup List!", self.parent.lines)
        self.clear()
        for line_entry in self.parent.lines:
            self.createLineEntry(line_entry['label'])
            # self.addItem(line_entry['label'])
        # self.itemClicked.connect(self.clicked)
        self.setMinimumWidth(self.sizeHintForColumn(0))


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