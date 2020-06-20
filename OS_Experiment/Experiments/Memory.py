KB = 1024


class MainMemory:
    def __init__(self):
        self.capacity = 512 * KB
        self.Partition_TableItems = []
        self.MaxLoads = 5
        self.Init_distribute()

    def Init_distribute(self):
        self.Partition_TableItems = []
        self.Partition_TableItems.append(
            [int(self.capacity / KB), 0, '空闲'])

    # 内存道数
    def ChangeLoads(self, loadNum):
        self.MaxLoads = loadNum
