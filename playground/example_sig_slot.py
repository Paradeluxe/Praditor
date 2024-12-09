from PySide6.QtCore import QObject, Signal, Slot

class MyObject(QObject):
    # 定义一个信号
    valueChanged = Signal(str)
    print(1)
    def __init__(self, startval="42"):
        super().__init__()
        self.ppval = startval
        print(2)

    @Slot(str)
    def setPP(self, val):
        if self.ppval != val:
            self.ppval = val
            # 发射信号
            self.valueChanged.emit(self.ppval)
            print(3)

    @Slot()
    def importAudio(self, fpath):
        if self.current_fpath != fpath:
            self.current_fpath = fpath
            self.valueChanged.emit(self.current_fpath)

    def print_this(self):
        print("my")

# 创建对象
obj = MyObject()
print(4)
# 连接信号到槽
obj.valueChanged.connect(obj.print_this)
print(5)
# 改变值，这将发射信号
obj.setPP("47")
obj.setPP("47")
obj.setPP("43")