from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background: white;
            }
        """)
        self.label = None
        # 创建QLabel实例
        self.label = QLabel(self)
        self.label.setWindowIcon(QIcon())

        # 加载图片
        pixmap = QPixmap("instruction.png")  # 替换为你的图片路径

        # print(pixmap.size())
        # 设置QLabel显示图片

        self.label.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())
        # self.setWindowIcon(QIcon())
        # 创建布局并添加QLabel
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 设置窗口标题和大小
        self.setWindowTitle('Parameters')
        self.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    ex = Example()
    app.exec()