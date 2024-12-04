from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMainWindow
from PySide6.QtCore import Qt

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel("Custom Title", self)
        self.title.setStyleSheet("font-weight: bold;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Title Bar")
        self.resize(400, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        central_widget = QWidget()
        self.title_bar = CustomTitleBar(self)
        work_space_layout = QVBoxLayout()
        work_space_layout.setContentsMargins(11, 11, 11, 11)
        work_space_layout.addWidget(QLabel("Hello, World!", self))
        centra_widget_layout = QVBoxLayout()
        centra_widget_layout.setContentsMargins(0, 0, 0, 0)
        centra_widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        centra_widget_layout.addWidget(self.title_bar)
        centra_widget_layout.addLayout(work_space_layout)
        central_widget.setLayout(centra_widget_layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()