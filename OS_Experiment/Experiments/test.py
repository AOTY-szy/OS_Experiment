from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication)

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
    def getCheckItem(self):
        #getCheckItem可以获得选择的项目text
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems
    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item)
        return checkedItems


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.checkableComboBox = CheckableComboBox(self)

        self.initUI()

    def initUI(self):
        itemList = ['项目1', '项目2', '项目3']
        for index, element in enumerate(itemList):
            self.checkableComboBox.addItem(element)
            item = self.checkableComboBox.model().item(index, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.checkableComboBox.move(100, 100)

        btn = QPushButton(self)
        btn.move(200, 100)
        btn.clicked.connect(self.sh)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')
        self.show()

    def sh(self):
        print(self.checkableComboBox.getCheckItem())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())