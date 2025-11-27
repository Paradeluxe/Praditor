from PySide6.QtWidgets import (
    QGridLayout, QApplication, QMainWindow, QWidget, QPushButton)


class ParamButtons(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle('Slider App')
        # self.setFixedHeight(100)
        layout = QGridLayout()
        layout.setSpacing(0)

        self.save_single_button = QPushButton("Save | Current")
        # self.save_single_button.setCheckable(True)
        # self.save_single_button.setChecked(True)
        # self.save_single_button.toggle()
        self.save_single_button.setMinimumHeight(30)
        layout.addWidget(self.save_single_button, 1, 0)


        self.show_single_button = QPushButton("Reset | Current")
        self.show_single_button.setMinimumHeight(30)
        layout.addWidget(self.show_single_button, 1, 1)

        self.run_single_button = QPushButton("Run | Current")
        self.run_single_button.setMinimumHeight(30)
        layout.addWidget(self.run_single_button, 1, 2)



        self.save_default_button = QPushButton("Save | Default")
        self.save_default_button.setMinimumHeight(30)
        layout.addWidget(self.save_default_button, 1, 3)

        self.show_default_button = QPushButton("Reset | Default")
        self.show_default_button.setMinimumHeight(30)
        layout.addWidget(self.show_default_button, 1, 4)

        self.run_default_button = QPushButton("Run | Default")
        self.run_default_button.setMinimumHeight(30)
        layout.addWidget(self.run_default_button, 1, 5)








        self.prev_button = QPushButton("Prev")
        # self.prev_button.setChecked(False)
        # self.prev_button.toggle()
        self.prev_button.setMinimumHeight(50)
        self.prev_button.setCheckable(True)
        layout.addWidget(self.prev_button, 0, 0)

        self.confirm_button = QPushButton("Confirm")
        # self.confirm_button.setChecked(False)
        # self.confirm_button.toggle()
        self.confirm_button.setMinimumHeight(30)
        layout.addWidget(self.confirm_button, 0, 1)

        self.next_button = QPushButton("Next")
        # self.show_default_button.setCheckable(True)
        # self.next_button.setChecked(False)
        # self.next_button.toggle()
        self.next_button.setMinimumHeight(30)
        layout.addWidget(self.next_button, 0, 2)

        # self.test_toggle_button = QToggleButton()


        container = QWidget()
        container.setLayout(layout)

        container.setStyleSheet("""
            QPushButton {
                background-color: ; 
                color: white; 
                border: 2px solid #1991D3;
                border-radius: 5px;
                margin: 4px

            }
            QPushButton:hover {
                background: red; 
                color: #1991D3;
                font-weight: bold;
                
            }
            QPushButton:checked {
                background: #1991D3; 
                color: white;
                font-weight: bold;
            }

            
        """)


        self.setCentralWidget(container)





if __name__ == '__main__':
    app = QApplication()
    ins = ParamButtons()
    ins.show()
    app.exec()