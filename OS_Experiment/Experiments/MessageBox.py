from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRect, QTimer, QElapsedTimer, pyqtSignal, QObject


class PCB_MessageBox(QMessageBox):
    def __init__(self, FLAG):
        super().__init__()

        self.setWindowTitle('PCB Contetns!')
        self.setStyleSheet('background-color:white')
        self.setWindowIcon(QIcon(r'..\Icons\contents.png'))

        self.YesBtn = QPushButton('FINISH')
        self.addButton(self.YesBtn, QMessageBox.YesRole)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setStyleSheet(
            "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
            "}"
            "QTableWidget{margin:5px}"
        )

        # Add TableWidget to QMessageBox
        if FLAG:
            self.addTableWidget(
                ['Name', 'Time(s)', 'Priority', 'Status', 'Attribution', 'Predecessor', 'Successor'])
        else:
            self.addTableWidget(['Name', 'Time(s)', 'Priority', 'Status', 'Attribution'])

    def addTableWidget(self, label):
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setGeometry(QRect(0, 0, 600, 80))
        self.tableWidget.setColumnCount(len(label))
        self.tableWidget.setRowCount(1)
        self.tableWidget.setHorizontalHeaderLabels(label)
        self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def event(self, e):
        result = QMessageBox.event(self, e)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(600, 120)

        return result

    def Stuffing(self, num, *args):
        for i in range(num):
            item = QTableWidgetItem(str(args[i]))
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(0, i, item)

class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
    def getCheckItem(self):
        #getCheckItem可以获得选择的项目text
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems
    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item)
        return checkedItems