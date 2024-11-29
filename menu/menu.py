import sys

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar, QApplication
)


class PraditorMenu(QMainWindow):
    valueChanged = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Praditor")
        self.setMinimumSize(1200, 800)
        self.setStatusBar(QStatusBar(self))
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 隐藏title bar
        self.setStyleSheet("""
            QMainWindow {
                background-color: #232323; /* 设置所有QWidget的底色为白色 */

            }

        """)

        # 菜单部分
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        button_action = QAction("&Read from folder...", self)
        button_action.setStatusTip("Folder to store target audios")
        # button_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(button_action)

        # file_menu.addAction(button_action)

        file_menu = menu.addMenu("&Show")
        button_action = QAction("&Onset", self)
        button_action.setCheckable(True)
        button_action.setStatusTip("Show Onset Results and Parameters")
        # button_action.triggered.connect(self.onMyToolBarButtonClick)
        file_menu.addAction(button_action)

        button_action = QAction("&Offset", self)
        button_action.setStatusTip("Show Offset Results and Parameters")
        button_action.setCheckable(True)
        # button_action.triggered.connect(self.onMyToolBarButtonClick)
        file_menu.addAction(button_action)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()


    # window.setStyleSheet("QWidget { background-color: white; }")
    # apply_stylesheet(app, theme='light_teal_500.xml', invert_secondary=True)
    window.show()

    app.exec()