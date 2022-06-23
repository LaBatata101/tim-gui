import sys
from PySide6 import QtCore, QtWidgets, QtGui
from tim_gui.api import TimAPI
from tim_gui.gui.windows import ItemsList, LoginWindow, MainWindow, ItemView
from decimal import Decimal


# class HelloWorld(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.button = QtWidgets.QPushButton("Push me!")
#         self.text = QtWidgets.QLabel("Hello World!", alignment=QtCore.Qt.AlignCenter)
#
#         self.layout = QtWidgets.QVBoxLayout(self)
#         self.layout.addWidget(self.text)
#         self.layout.addWidget(self.button)
#
#         self.button.clicked.connect(self.magic)
#
#     @QtCore.Slot()
#     def magic(self):
#         print("magic")
        # self.text.setText("<b>Hello World!</b>")

def run():
    api = TimAPI()
    api.login(username="admin@admin.com", password="admin")
    app = QtWidgets.QApplication()

    # login = LoginWindow(api, "Login")
    # login.show()

    window = MainWindow(api)
    window.resize(500, 500)
    window.showMaximized()

    sys.exit(app.exec())
