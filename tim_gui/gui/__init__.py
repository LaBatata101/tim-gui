import sys

from PySide6 import QtWidgets

from tim_gui.api import TimAPI
from tim_gui.gui.windows import LoginWindow


def run():
    api = TimAPI()
    app = QtWidgets.QApplication()

    login = LoginWindow(api)
    login.show()

    sys.exit(app.exec())
