import math
from Experiments.MessageBox import *


class MyQPushButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.process = None

    def Set_Parent_Process(self, process):
        self.process = process


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 左上控件
        self.Predecessor_Lable = QLabel("Predecessor:")
        self.Predecessor_ComBox = CheckableComboBox()
        self.Successor_Label = QLabel("Successor:")
        self.Successor_ComBox = CheckableComboBox()
        self.nameLineEdit = QLineEdit()
        shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        shortcut.activated.connect(self.nameLineEdit.setFocus)

        self.priorityLineEdit = QLineEdit()
        self.timeLineEdit = QLineEdit()
        self.sizeLineEdit = QLineEdit()
        self.HiddenHb = QHBoxLayout()
        self.HiddenHb.addWidget(self.Predecessor_Lable, alignment=Qt.AlignLeft)
        self.HiddenHb.addWidget(self.Predecessor_ComBox, alignment=Qt.AlignCenter)
        self.HiddenHb.addWidget(self.Successor_Label, alignment=Qt.AlignCenter)
        self.HiddenHb.addWidget(self.Successor_ComBox, alignment=Qt.AlignLeft)
        self.RadioBtn1 = QRadioButton('Independent')
        self.RadioBtn2 = QRadioButton('Synchronised')
        self.SubmitBtn = QPushButton(QIcon(r'..\Icons\\submit.png'), "Submit")
        self.ClearBtn = QPushButton(QIcon(r'..\Icons\clear.png'), "Clear")

        self.Predecessor_ComBox.setFixedWidth(65)
        self.Successor_ComBox.setFixedWidth(65)

        # 右下控件
        self.Partiton_TB = QTabWidget()
        self.Partition_Table = self.Partition_Table_Settings()

        # 右上控件
        self.Tables = [None] * 4
        self.tab = QTabWidget()
        self.Tables[0] = QTableWidget()
        self.Tables[1] = QTableWidget()
        self.Tables[2] = QTableWidget()
        self.Tables[3] = QTableWidget()

        # 左下控件
        self.LoadEdit = QSpinBox()
        self.Processor_Num_Box = QSpinBox()
        self.MemorySize = QComboBox()
        self.LoadEdit.setKeyboardTracking(False)
        self.Processor_Num_Box.setKeyboardTracking(False)

        self.InitUI()

    def InitUI(self):
        self.setWindowTitle("Operating System Experiment")
        self.setWindowIcon(QIcon(r'..\Icons\icon.png'))

        # 窗口居中显示
        self.resize(980, 600)
        qt = self.frameGeometry()
        qt.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(qt.topLeft())

        self.tab.addTab(self.Table_Settings(self.Tables[0],
                                            ['Process Name', 'Priority', 'Processor', 'Rate of progress', '', '']),
                        "RUNNING")
        self.tab.addTab(
            self.Table_Settings(self.Tables[1], ['Process Name', 'Priority', 'Rate of progress', '', '']), "READY")
        self.tab.addTab(
            self.Table_Settings(self.Tables[2], ['Process Name', 'Priority', 'Rate of progress', '', '']),
            "SUSPENDED")
        self.tab.addTab(
            self.Table_Settings(self.Tables[3], ['Process Name', 'Priority', 'Rate of progress', '', '']),
            "RESERVED")

        # 显示主存的一些信息
        SetGB = QGroupBox("Basic Settings")
        SetGB.setLayout(self.Memory_Info_Settings())

        # 添加一个新的进程
        InputGroupBox = QGroupBox("Add Process")
        # InputGroupBox.setFixedWidth(300)
        InputGroupBox.setLayout(self.FormSettings())

        # 空闲分区表的显示
        self.Partiton_TB.addTab(self.Partition_Table, 'Free partition table')

        hb1 = QHBoxLayout()
        hb1.addWidget(InputGroupBox)
        hb1.addWidget(self.tab)

        hb2 = QHBoxLayout()
        hb2.addWidget(SetGB)
        hb2.addWidget(self.Partiton_TB)

        vb = QVBoxLayout()
        vb.addLayout(hb1)
        vb.addLayout(hb2)

        self.setLayout(vb)

        self.show()

    def FormSettings(self):
        grid = QGridLayout()
        # 进程名
        nameLabel = QLabel("Input process name(_E):")
        self.nameLineEdit.setMaximumWidth(100)
        # 优先权
        priorityLabel = QLabel("Input Priority:")
        self.priorityLineEdit.setMaximumWidth(30)
        # 运行时间
        timeLabel = QLabel("Input required time:")
        self.timeLineEdit.setMaximumWidth(40)
        TunitLabel = QLabel("(S)")
        TunitLabel.setMargin(10)

        sizeLabel = QLabel("Input process size:")
        self.sizeLineEdit.setMaximumWidth(40)
        SunitLabel = QLabel("(KB)")
        SunitLabel.setMargin(10)

        # 控件布局
        grid.addWidget(nameLabel, 0, 0)
        grid.addWidget(self.nameLineEdit, 0, 1, 1, 2)
        grid.addWidget(priorityLabel, 1, 0)
        grid.addWidget(self.priorityLineEdit, 1, 1)
        grid.addWidget(timeLabel, 2, 0)
        grid.addWidget(self.timeLineEdit, 2, 1)
        grid.addWidget(TunitLabel, 2, 2)
        grid.addWidget(sizeLabel, 3, 0)
        grid.addWidget(self.sizeLineEdit, 3, 1)
        grid.addWidget(SunitLabel, 3, 2)

        # 进程属性
        attributesLabel = QLabel("Choose attribute:")
        self.RadioBtn1.setChecked(True)
        self.RadioBtn2.toggled.connect(self.ShowCombox)
        hb = QHBoxLayout()
        hb.addWidget(attributesLabel)
        hb.addWidget(self.RadioBtn1)
        hb.addSpacing(1)
        hb.addWidget(self.RadioBtn2)
        grid.addLayout(hb, 4, 0, 1, 3)

        # 隐藏下拉框
        self.setStatus(False)
        grid.addLayout(self.HiddenHb, 5, 0, 1, 3)
        self.SubmitBtn.setMaximumWidth(63)
        self.ClearBtn.setMaximumWidth(63)

        hb = QHBoxLayout()
        hb.addSpacing(1)
        hb.addWidget(self.SubmitBtn)
        hb.addSpacing(1)
        hb.addWidget(self.ClearBtn)
        hb.addSpacing(1)
        grid.addLayout(hb, 6, 0, 1, 3)
        return grid

    def setStatus(self, FLAG):
        self.Predecessor_Lable.setVisible(FLAG)
        self.Predecessor_ComBox.setVisible(FLAG)
        self.Successor_Label.setVisible(FLAG)
        self.Successor_ComBox.setVisible(FLAG)

    def ShowCombox(self):
        sender = self.sender()
        if sender.isChecked():
            self.setStatus(True)
            # 往ComBox里面添加进程名
        else:
            self.setStatus(False)

    @staticmethod
    def Partition_Table_Settings():
        Partition_Table = QTableWidget()
        Partition_Table.setRowCount(8)
        Partition_Table.setColumnCount(4)
        Partition_Table.setHorizontalHeaderLabels(
            ['Partition number', 'Partition Size (KB)', 'Starting Address', 'Status'])
        Partition_Table.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)
        Partition_Table.setVerticalScrollMode(Partition_Table.ScrollPerPixel)
        Partition_Table.verticalHeader().setVisible(False)
        Partition_Table.setEditTriggers(QTableView.NoEditTriggers)
        Partition_Table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        Partition_Table.setStyleSheet(
            "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
            "}"
        )
        Partition_Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return Partition_Table

    @staticmethod
    def Table_Settings(Qtable, HeaderLabels):
        Qtable.setRowCount(10)
        Qtable.setColumnCount(len(HeaderLabels))
        Qtable.setHorizontalHeaderLabels(HeaderLabels)
        Qtable.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)
        Qtable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        Qtable.setRowHeight(0, 10)
        Qtable.setVerticalScrollMode(Qtable.ScrollPerPixel)
        Qtable.verticalHeader().setVisible(False)
        Qtable.setEditTriggers(QTableView.NoEditTriggers)
        Qtable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        Qtable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        Qtable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        Qtable.setStyleSheet(
            "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
            "}"
        )
        if len(HeaderLabels) == 6:
            Qtable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        return Qtable

    def Memory_Info_Settings(self):
        label = QLabel("Set the specified number of loads:")
        label2 = QLabel("(道)")
        self.LoadEdit.setMaximumWidth(50)
        self.LoadEdit.setKeyboardTracking(False)
        self.LoadEdit.setRange(1, 10)
        self.LoadEdit.setValue(5)
        hb = QHBoxLayout()
        hb.addWidget(label)
        hb.addWidget(self.LoadEdit)
        hb.addWidget(label2)

        label = QLabel("Set the size of the memory:")
        label2 = QLabel("(KB)")
        for i in range(8, 14):
            self.MemorySize.addItem(str(int(math.pow(2, i))))
        self.MemorySize.setCurrentText('512')
        hb1 = QHBoxLayout()
        hb1.addWidget(label)
        hb1.addWidget(self.MemorySize)
        hb1.addWidget(label2)

        label = QLabel("Set the number of processor:")
        label2 = QLabel("(个)")
        self.Processor_Num_Box.setMaximumWidth(50)
        self.Processor_Num_Box.setStyleSheet("QSpinBox:{margin:5px}")
        self.Processor_Num_Box.setKeyboardTracking(False)
        self.Processor_Num_Box.setRange(1, 2)
        self.Processor_Num_Box.setValue(1)
        hb2 = QHBoxLayout()
        hb2.addWidget(label)
        hb2.addWidget(self.Processor_Num_Box)
        hb2.addWidget(label2)

        vb = QVBoxLayout()
        vb.addLayout(hb)
        vb.addLayout(hb2)
        vb.addLayout(hb1)

        return vb
