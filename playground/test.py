from PySide6.QtCore import QObject, Signal, Property

class MyModel(QObject):
    # 定义信号（不需要参数）
    data_changed = Signal()

    def __init__(self):
        super().__init__()
        self._my_variable = {"onset": [], "offset": []}  # 私有变量

    @Property(dict)  # 指定类型（可选）
    def my_variable(self):
        return self._my_variable

    @my_variable.setter
    def my_variable(self, value):
        if self._my_variable != value:  # 只有值变化时才触发
            self._my_variable = value
            self.data_changed.emit()  # 触发信号

# 使用示例
model = MyModel()

# 连接信号到槽
model.data_changed.connect(lambda: print(f"值已改变: {model.my_variable}"))

# 修改变量（触发信号）
model.my_variable = {1:1}