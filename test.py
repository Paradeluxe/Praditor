import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar
import webbrowser
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        # 创建一个菜单
        menu = self.menuBar.addMenu('&文件')

        # 创建一个动作（QAction），并设置其触发时执行的操作
        openWebAction = QAction('打开网页', self)
        openWebAction.triggered.connect(self.openWebPage)

        # 将动作添加到菜单中
        menu.addAction(openWebAction)

    def openWebPage(self):
        # 使用webbrowser模块打开默认浏览器并导航到指定网址
        webbrowser.open('https://www.example.com')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())