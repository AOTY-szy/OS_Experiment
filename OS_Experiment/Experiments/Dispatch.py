from Experiments.MainWindow import *
from Experiments.Memory import *
from Experiments.PCB import PCB
import sys

RUNNING = 0
READY = 1
SUSPENDED = 2
RESERVED = 3

PID = [i for i in range(1, 1000)]


def getPID():
    return PID.pop(0)


def recyclePID(i):
    PID.insert(0, i)


def Status_Convert(i: int):
    if i == 0:
        return 'RUNNING'
    elif i == 1:
        return 'READY'
    elif i == 2:
        return 'SUSPENDED'
    else:
        return 'RESERVED'


class Process():
    def __init__(self, pbtn: QPushButton, cbtn, pbar, **kwargs):
        self.pcb_btn = pbtn
        self.control_btn = cbtn
        self.process_bar = pbar
        self.process_bar.setStyleSheet('QProgressBar:horizontal{border: 1px solid gray;border-radius: 3px;background: white;padding: 1px;margin: 1.2px} \
        QProgressBar::chunk:horizontal')
        self.process_bar.setAlignment(Qt.AlignCenter)
        self.pcb_btn.setStyleSheet('QPushButton{margin:2px}')
        self.control_btn.setStyleSheet('QPushButton{margin:2px}')
        self.PCB = PCB(**kwargs)

        self.control_btn.Set_Parent_Process(self)
        self.pcb_btn.clicked.connect(lambda: self.showPCB(self))

    @staticmethod
    def showPCB(process):
        kind = False if process.PCB.attribution == 'Independent' else True
        pcb_msg = PCB_MessageBox(kind)
        length = 7 if kind else 5
        pcb_msg.Stuffing(length,
                         *[process.PCB.name, round(process.PCB.time, 2), process.PCB.priority,
                           Status_Convert(process.PCB.status),
                           process.PCB.attribution,
                           ' '.join(pre.PCB.name for pre in process.PCB.predecessor) if process.PCB.predecessor else None,
                           ' '.join(suc.PCB.name for suc in process.PCB.successor) if process.PCB.successor else None][
                          0:length])
        pcb_msg.exec()


class Processor(QObject):
    Scheduling_signal = pyqtSignal()

    @staticmethod
    def Examine(*args):
        if args[0] == '':
            return 1
        elif args[1] == '' or eval(args[1]) <= 0 or int(eval(args[1])) != eval(args[1]):
            return 2
        elif args[2] == "" or eval(args[2]) <= 0:
            return 3
        elif args[3] == '' or eval(args[3]) <= 0:
            return 4
        else:
            return 0

    def __init__(self):
        super().__init__()

        self.Process = [[], [], [], []]

        self.Synchronised_PID = []

        self.window = MyWindow()

        self.num = 1
        self.timeslices = [0] * 2
        self.Memory_Process_Nums = 0

        self.memory = MainMemory()
        self.Partition_Table_Update()

        self.clk = QTimer()
        # 被抢占退出时获得运行时间
        self.elaclks = [QElapsedTimer(), QElapsedTimer()]

        # 绑定信号与槽
        self.Binding()

    def Binding(self):
        self.window.SubmitBtn.clicked.connect(self.CreateProcess)
        self.window.ClearBtn.clicked.connect(self.ClearContents)
        self.window.LoadEdit.editingFinished.connect(lambda: self.memory.ChangeLoads(self.window.LoadEdit.value()))
        self.window.Processor_Num_Box.editingFinished.connect(
            lambda: self.NumChange(self.window.Processor_Num_Box.value()))
        self.window.MemorySize.currentIndexChanged[str].connect(self.ChangeCapacity)
        self.clk.timeout.connect(self.ProcessBar_Update)
        self.Scheduling_signal.connect(lambda: self.Preemptive_Priority_Scheduling(self.Process[READY][0]))

    def NumChange(self, num):
        self.num = num

    # 内存容量
    def ChangeCapacity(self, text):
        self.memory.capacity = int(text) * KB
        self.memory.Init_distribute()
        self.Partition_Table_Update()

    def ClearContents(self):
        self.window.nameLineEdit.setText('')
        self.window.priorityLineEdit.setText('')
        self.window.timeLineEdit.setText('')
        self.window.sizeLineEdit.setText('')
        self.window.RadioBtn1.setChecked(True)

        self.window.Predecessor_ComBox.setCurrentIndex(-1)
        self.window.Successor_ComBox.setCurrentIndex(-1)

    # 更新空闲分区表
    def Partition_Table_Update(self, StartLocations=[], Lengths=[]):
        self.window.Partiton_TB.removeTab(0)
        self.window.Partition_Table = MyWindow.Partition_Table_Settings()
        self.window.Partiton_TB.addTab(self.window.Partition_Table, 'Free partition table')
        # 根据始址进行排序
        self.memory.Partition_TableItems.sort(key=lambda x: x[1])


        # 回收内存
        if len(StartLocations):
            for start, size in zip(StartLocations, Lengths):
                idx = next((idx for idx, x in enumerate(self.memory.Partition_TableItems) if x[1] > start), -1)
                if idx == 0:
                    if start + size * KB == self.memory.Partition_TableItems[idx][1]:
                        self.memory.Partition_TableItems.insert(0, [size, start, '空闲'])
                        self.memory.Partition_TableItems[0][0] += self.memory.Partition_TableItems[1][0]
                        del self.memory.Partition_TableItems[1]
                    else:
                        self.memory.Partition_TableItems.insert(0, [size, start, '空闲'])
                elif idx == -1:
                    if self.memory.Partition_TableItems[-1][1] + self.memory.Partition_TableItems[-1][0] * KB == start:
                        self.memory.Partition_TableItems[-1][0] += size
                    else:
                        self.memory.Partition_TableItems.append([size, start, '空闲'])
                else:
                    # 和前相邻
                    if self.memory.Partition_TableItems[idx - 1][0] * KB + self.memory.Partition_TableItems[idx - 1][
                        1] == start:
                        # 和后相邻
                        if start + size * KB == self.memory.Partition_TableItems[idx][1]:
                            self.memory.Partition_TableItems[idx - 1][0] += (
                                    size + self.memory.Partition_TableItems[idx][0])
                            del self.memory.Partition_TableItems[idx]
                        # 和前相邻不和后相邻
                        else:
                            self.memory.Partition_TableItems[idx - 1][0] += size
                    # 不和前相邻但是和后相邻
                    elif start + size * KB == self.memory.Partition_TableItems[idx][1]:
                        self.memory.Partition_TableItems.insert(idx,
                                                                [size + self.memory.Partition_TableItems[idx][0], start,
                                                                 '空闲'])
                        del self.memory.Partition_TableItems[idx + 1]
                    # 既不和前相邻又不和后相邻
                    else:
                        self.memory.Partition_TableItems.insert(idx, [size, start, '空闲'])


        current_Row_Counts = self.window.Partition_Table.rowCount()
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignCenter)
        for i, row in enumerate(self.memory.Partition_TableItems):
            if i == current_Row_Counts:
                self.window.Partition_Table.insertRow(current_Row_Counts)
                current_Row_Counts += 1
            for j in range(4):
                stuffingItem = item.clone()
                if j == 0:
                    stuffingItem.setText(str(i + 1))
                elif j == 2:
                    stuffingItem.setText("0x{:08X}H".format(row[j - 1]))
                else:
                    stuffingItem.setText(str(row[j - 1]))
                self.window.Partition_Table.setItem(i, j, stuffingItem)

    def CreateProcess(self):
        size = self.window.sizeLineEdit.text()
        priority = self.window.priorityLineEdit.text()
        name = self.window.nameLineEdit.text()
        time = self.window.timeLineEdit.text()
        status = self.Examine(name, priority, time, size)
        pre = []
        suc = []
        if not status:
            pid = getPID()
            priority, time, size = int(priority), eval(time), eval(size)
            contents = {
                "name": name,
                "priority": priority,
                "time": time,
                'totaltime': time,
                "pid": pid,
                "address": None,
                "size": size,
                "status": RESERVED,
                "predecessor": [],
                "successor": [],
                'processor': None,
                "attribution": "Independent"
            }
            if self.window.RadioBtn2.isChecked():
                contents['attribution'] = "Synchronised"
                checkedItems = self.window.Predecessor_ComBox.getCheckItem()
                if checkedItems:
                    ProcessNames = []
                    for i in range(self.window.Predecessor_ComBox.count()):
                        ProcessNames.append(self.window.Predecessor_ComBox.itemText(i))
                    for item in checkedItems:
                        pre.append(list(filter(
                            lambda x: x.PCB.pid == self.Synchronised_PID[ProcessNames.index(item)],
                            self.Process[RUNNING] + self.Process[RESERVED] + self.Process[SUSPENDED] + self.Process[
                                READY]))[0])
                        contents['predecessor'].append(pre[-1])

                checkedItems = self.window.Successor_ComBox.getCheckItem()
                if checkedItems:
                    ProcessNames = []
                    for i in range(self.window.Successor_ComBox.count()):
                        ProcessNames.append(self.window.Successor_ComBox.itemText(i))
                    for item in checkedItems:
                        suc.append(list(filter(lambda x: x == self.Synchronised_PID[ProcessNames.index(item)],
                                      self.Process[RUNNING] + self.Process[RESERVED] + self.Process[SUSPENDED] +
                                      self.Process[READY]))[0])
                        contents['successor'].append(suc[-1])

                self.ADD_Selected_Items(name, pid)

            # 消息提示
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowIcon(QIcon(r"..\Icons\ok.png"))
            msg.setWindowTitle("Submit successfully!")
            msg.setStyleSheet('background-color:white')
            msg.setText("You have added one process into the computer!")
            msg.exec()
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setEscapeButton(QMessageBox.Ok)
            self.Process[RESERVED].append(Process(*self.ADD_Buttons("Revocate"), **contents))
            for pro in pre:
                pro.PCB.successor.append(self.Process[RESERVED][-1])
            for pro in suc:
                pro.PCB.predecessor.append(self.Process[RESERVED][-1])
            self.Table_Update(RESERVED, ['Process Name', 'Priority', 'Rate of progress', '', ''], False)

            self.ClearContents()
            self.Enter_Memory()

        else:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(r'..\Icons\wrong.png'))
            msg.setWindowTitle("Error Alert!")
            if status == 1:
                self.window.nameLineEdit.setFocus()
                msg.setText("Proceess name cannot be empty!")
            elif status == 2:
                self.window.priorityLineEdit.setFocus()
                msg.setText("The priority must be a positive integer!")
            elif status == 3:
                self.window.timeLineEdit.setFocus()
                msg.setText("Required run-time must be a positive number!")
            else:
                self.window.sizeLineEdit.setFocus()
                msg.setText("Process size must be a positive number!")
            msg.setStyleSheet('background-color:white')
            msg.setStandardButtons(QMessageBox.Close)
            msg.setEscapeButton(QMessageBox.Close)
            msg.exec()

    def ADD_Selected_Items(self, name, pid):
        self.window.Successor_ComBox.addItem(name)
        self.window.Successor_ComBox.setCurrentIndex(-1)

        self.window.Predecessor_ComBox.addItem(name)
        self.window.Predecessor_ComBox.setCurrentIndex(-1)
        self.Synchronised_PID.append(pid)

    def Shift(self, process, label, OldStatue, NewStatus, Oldslot, Newslot):
        self.Process[OldStatue].remove(process)
        self.Process[NewStatus].append(process)
        process.PCB.status = NewStatus
        process.control_btn.clicked.disconnect(Oldslot)
        process.control_btn.clicked.connect(Newslot)
        process.control_btn.setText(label)

    # 进度条更新
    def ProcessBar_Update(self):
        self.clk.stop()
        processorSerials = []
        flag = True
        for process in self.Process[RUNNING]:
            process.PCB.time -= 0.2
            self.timeslices[process.PCB.processor - 1] -= 1
            process.process_bar.setValue(
                min(100, (process.PCB.totaltime - process.PCB.time) / process.PCB.totaltime * 100))
            processorSerials.append(process.PCB.processor)
            # 进程结束了，可以选择一个后备进程加入进来
            if process.PCB.time <= 0:
                self.Exit_Management(process)
                for pro in self.Process[RESERVED]:
                    if self.Memory_Process_Nums >= self.memory.MaxLoads:
                        break
                    else:
                        start_address = self.FF(pro.PCB.size)  # 能够获得所需要的内存空间
                        if start_address is not None:
                            self.Partition_Table_Update()
                            pro.PCB.address = start_address
                            pro.PCB.status = READY
                            self.Shift(pro, 'Suspend', RESERVED, READY, self.Revocate_Process, self.Suspend)
                            self.Memory_Process_Nums += 1
                            self.Table_Update(RESERVED, ['Process Name', 'Priority', 'Rate of progress', '', ''], True,
                                              READY)
                self.Preemptive_Priority_Scheduling()
                flag = False
            # 时间片用完了
            elif self.timeslices[process.PCB.processor - 1] <= 0:
                self.Shift(process, 'Suspend', RUNNING, READY, self.Cancel, self.Suspend)
                process.PCB.processor = None
                self.Table_Update(RUNNING, ['Process Name', 'Priority', 'Processor', 'Rate of progress', '', ''], True,
                                  READY)
                self.Preemptive_Priority_Scheduling()
                flag = False
        for serial in processorSerials:
            self.elaclks[serial - 1].restart()
        if flag:
            self.clk.start(200)

    def Exit_Management(self, process):
        # 清除该进程并回收内存
        self.Revocate_Process(process)
        self.Memory_Process_Nums -= 1

        self.Table_Update(RUNNING, ['Process Name', 'Priority', 'Processor', 'Rate of progress', '', ''])
        self.Partition_Table_Update([process.PCB.address], [process.PCB.size])

    def AddInfo(self, process):
        if len(self.Process[RUNNING]) == 0:
            process.PCB.processor = 1
        else:
            numbers = [1, 2]
            numbers.remove([pro.PCB.processor for pro in self.Process[RUNNING]][0])
            process.PCB.processor = numbers[0]

        # 分配一个时间片
        self.timeslices[process.PCB.processor - 1] = 5

        self.Shift(process, 'Cancel', READY, RUNNING, self.Suspend, self.Cancel)

        process.PCB.priority += 1

        self.Table_Update(READY, ['Process Name', 'Priority', 'Rate of progress', '', ''],
                          True,
                          RUNNING)

    def Preemptive_Priority_Scheduling(self, process=None):
        self.clk.stop()
        # 正常调度
        flag = False
        if process is None:
            # 找到优先级最高且能够接受调度的进程
            for _ in range(self.num - len(self.Process[RUNNING])):
                for process in self.Process[READY]:
                    if not process.PCB.predecessor:
                        flag = True
                        break
                if flag:
                    self.AddInfo(process)
                    flag = False
        # 有新的进程进入内存
        elif not process.PCB.predecessor:
            if len(self.Process[RUNNING]) == self.num:
                RunningPro = self.Process[RUNNING][-1]
                cmp = process.PCB.priority - RunningPro.PCB.priority
                if cmp < 0:
                    # 处理机抢占
                    self.Shift(RunningPro, 'Suspend', RUNNING, READY, self.Cancel, self.Suspend)
                    self.Shift(process, 'Cancel', READY, RUNNING, self.Suspend, self.Cancel)

                    RunningPro.PCB.time -= self.elaclks[RunningPro.PCB.processor - 1].elapsed() / 1000
                    if RunningPro.PCB.time <= 0:
                        self.Exit_Management(RunningPro)

                    process.PCB.processor = RunningPro.PCB.processor
                    RunningPro.PCB.processor = None

                    # 分配一个时间片
                    self.timeslices[process.PCB.processor - 1] = 5

                    process.PCB.priority += 1

                    self.Table_Update(RUNNING,
                                      ['Process Name', 'Priority', 'Processor', 'Rate of progress', '', ''],
                                      True, READY)
            else:
                self.AddInfo(process)
        self.clk.start(200)

    # 分配内存空间
    def FF(self, size):
        for Item in self.memory.Partition_TableItems:
            # 首次适应算法
            if size <= Item[0]:
                ORGINTADDRESS = Item[1]
                # 修改空闲分区表
                if size == Item[0]:
                    self.memory.Partition_TableItems.remove(Item)
                else:
                    Item[0] = Item[0] - size
                    Item[1] += size * KB
                # 返回起始地址
                return ORGINTADDRESS
        return None

    def Enter_Memory(self):
        self.clk.stop()
        for process in self.Process[RESERVED]:
            if self.Memory_Process_Nums >= self.memory.MaxLoads:  # 未达到设置的主存的道数
                self.clk.start(200)
                return
            else:
                start_address = self.FF(process.PCB.size)  # 能够获得所需要的内存空间
                if start_address is not None:
                    self.Partition_Table_Update()
                    process.PCB.address = start_address
                    process.PCB.status = READY
                    self.Shift(process, 'Suspend', RESERVED, READY, self.Revocate_Process, self.Suspend)
                    self.Memory_Process_Nums += 1
                    self.Table_Update(RESERVED, ['Process Name', 'Priority', 'Rate of progress', '', ''], True, READY)
                    self.Scheduling_signal.emit()  # 有进程新加入到就绪队列当中 需要和正在运行的进程进行优先权对比

    def Active(self):
        sender = self.window.sender()
        process = sender.process
        process.PCB.address = self.FF(process.PCB.size)
        self.Partition_Table_Update()
        self.Shift(process, 'Suspend', SUSPENDED, READY, self.Active, self.Suspend)
        self.Table_Update(SUSPENDED, ['Process Name', 'Priority', 'Rate of progress', '', ''], True, READY)
        self.Scheduling_signal.emit()

    def Cancel(self):
        sender = self.window.sender()
        process = sender.process
        process.PCB.time -= self.elaclks[process.PCB.processor - 1].elapsed() / 1000
        process.PCB.processor = None
        self.Shift(process, "Suspend", RUNNING, READY, self.Cancel, self.Suspend)
        self.Table_Update(RUNNING, ['Process Name', 'Priority', 'Processor', 'Rate of progress', '', ''], True, READY)
        self.Scheduling_signal.emit()

    def Suspend(self):
        sender = self.window.sender()
        process = sender.process
        address = process.PCB.address
        process.PCB.address = None
        self.Memory_Process_Nums -= 1
        self.Shift(process, 'Active', READY, SUSPENDED, self.Suspend, self.Active)
        self.Table_Update(READY, ['Process Name', 'Priority', 'Rate of progress', '', ''], True, SUSPENDED)
        self.Partition_Table_Update([address], [process.PCB.size])
        for pro in self.Process[RESERVED]:
            if self.Memory_Process_Nums >= self.memory.MaxLoads:
                return
            else:
                start_address = self.FF(pro.PCB.size)  # 能够获得所需要的内存空间
                if start_address is not None:
                    self.Partition_Table_Update()
                    pro.PCB.address = start_address
                    pro.PCB.status = READY
                    self.Shift(pro, 'Suspend', RESERVED, READY, self.Revocate_Process, self.Suspend)
                    self.Memory_Process_Nums += 1
                    self.Table_Update(RESERVED, ['Process Name', 'Priority', 'Rate of progress', '', ''], True,
                                      READY)
        if pro:
            self.Preemptive_Priority_Scheduling(pro)

    def Revocate_Process(self, process=None):
        # 撤销改进程
        if not process:
            sender = self.window.sender()
            process = sender.process
        self.Process[process.PCB.status].remove(process)
        pid = process.PCB.pid
        recyclePID(pid)
        if process.PCB.attribution == 'Synchronised':
            index = self.Synchronised_PID.index(pid)
            self.Synchronised_PID.remove(pid)
            self.window.Predecessor_ComBox.removeItem(index)
            self.window.Successor_ComBox.removeItem(index)

            # 更新前驱、后继进程
            for proc in self.Process[RESERVED] + self.Process[READY] + self.Process[RUNNING] + \
                        self.Process[SUSPENDED]:
                if proc.PCB.successor and pid in [p.PCB.pid for p in proc.PCB.successor]:
                    proc.PCB.successor.remove(process)
                elif proc.PCB.predecessor and pid in [p.PCB.pid for p in proc.PCB.predecessor]:
                    proc.PCB.predecessor.remove(process)

        if process.PCB.status == RESERVED:
            self.Table_Update(RESERVED, ['Process Name', 'Priority', 'Rate of progress', '', ''], False)

    # 一层自调
    def Table_Update(self, kind, labels, FLAG=False, Subkind=None):
        title1 = Status_Convert(kind)
        self.window.tab.removeTab(kind)
        self.window.Tables[kind] = MyWindow.Table_Settings(QTableWidget(), labels)
        self.window.tab.insertTab(kind, self.window.Tables[kind], title1)
        # 切换界面
        self.window.tab.setCurrentIndex(kind)
        current_Row_Counts = self.window.Tables[kind].rowCount()
        self.Process[kind].sort(key=lambda pro: pro.PCB.priority)
        for i, process in enumerate(self.Process[kind]):
            if i == current_Row_Counts:
                self.window.Tables[kind].insertRow(current_Row_Counts)
                current_Row_Counts += 1
            item = QTableWidgetItem(str(process.PCB.priority))
            item.setTextAlignment(Qt.AlignCenter)
            self.window.Tables[kind].setItem(i, 0, QTableWidgetItem(process.PCB.name))
            self.window.Tables[kind].setItem(i, 1, item)
            j = 2
            if len(labels) == 6:
                processorItem = item.clone()
                processorItem.setText(str(process.PCB.processor))
                self.window.Tables[kind].setItem(i, j, processorItem)
                j += 1
            self.window.Tables[kind].setCellWidget(i, j, process.process_bar)
            j += 1
            self.window.Tables[kind].setCellWidget(i, j, process.pcb_btn)
            j += 1
            self.window.Tables[kind].setCellWidget(i, j, process.control_btn)
        if not FLAG:
            return
        else:
            self.Table_Update(Subkind, ['Process Name', 'Priority', 'Processor', 'Rate of progress', '',
                                        ''] if Subkind == RUNNING else ['Process Name', 'Priority', 'Rate of progress',
                                                                        '', ''])

    def ADD_Buttons(self, label):
        PCB_button = QPushButton()
        PCB_button.setText("PCB")
        btn = MyQPushButton()
        btn.clicked.connect(self.Revocate_Process)
        btn.setText(label)
        processBar = QProgressBar()
        processBar.setValue(0)
        return [PCB_button, btn, processBar]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    BOSS = Processor()
    sys.exit(app.exec_())
