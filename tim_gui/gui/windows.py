from decimal import Decimal
from typing import Type, Union

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QCompleter, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QMessageBox, QPushButton,
                               QScrollArea, QTextEdit, QVBoxLayout, QWidget)

from tim_gui.api import TimAPI
from tim_gui.api.models import Item, ItemUpdate

# TODO: Move custom widgets to different file


class LoginWindow(QWidget):
    def __init__(self, api: TimAPI, title: str = "", width: int = 500, height: int = 500):
        super().__init__()

        self.api = api

        self.setWindowTitle(title)
        self.setFixedSize(width, height)

        self.login_lbl = QLabel("Login")
        self.password_lbl = QLabel("Password")

        self.login_le = QLineEdit()
        self.password_le = QLineEdit()
        self.password_le.setEchoMode(QLineEdit.Password)

        self.signin_btn = QPushButton("Sign in")
        self.signin_btn.clicked.connect(self.sigin)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.login_lbl)
        v_layout.addWidget(self.login_le)
        v_layout.addWidget(self.password_lbl)
        v_layout.addWidget(self.password_le)
        v_layout.addWidget(self.signin_btn)

        self.setLayout(v_layout)

    def sigin(self):
        login_txt = self.login_le.text()
        password_txt = self.password_le.text()

        if not login_txt and not password_txt:
            QMessageBox.critical(self, "ERRO!", "Campo de login e senha não podem estar vazios!")
            return

        if not login_txt:
            QMessageBox.critical(self, "ERRO!", "Campo de login não pode estar vazio!")
            return

        if not password_txt:
            QMessageBox.critical(self, "ERRO!", "Campo da senha não pode estar vazio!")
            return

        try:
            self.api.login(username=login_txt, password=password_txt)
        except:
            QMessageBox.critical(self, "ERRO!", "login ou senha incorretos!")
            return

        self.close()

        self.main_window = MainWindow(self.api, "T.I.M")
        self.main_window.showMaximized()


class TableModel(QtCore.QAbstractTableModel):
    HORIZONTAL_LABELS = ["Title", "BarCode", "Description", "Price", "Image Path", "Quantity"]

    def __init__(self, data: list[Item]):
        super().__init__()
        self._data: list[list[Item]] = [list(d.dict(exclude={"id", "owner_id"}).values()) for d in data]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            data = self._data[index.row()][index.column()]
            if isinstance(data, Decimal):
                # print("DECIMAL")
                return str(data)
            return data

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return TableModel.HORIZONTAL_LABELS[section]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])


# class MainWindow(QWidget):
#     MINIMUM_WIDTH = 500
#     MINIMUM_HEIGHT = 500
#
#     def __init__(self, api: TimAPI, title: str = ""):
#         super().__init__()
#
#         self.api = api
#         self.setWindowTitle(title)
#         self.setMinimumSize(MainWindow.MINIMUM_WIDTH, MainWindow.MINIMUM_HEIGHT)
#
#         self.model = TableModel(self.api.items())
#
#         self.search_le = QLineEdit()
#         self.search_le.textChanged.connect(self.search)
#
#         self.table = QTableView()
#         self.table.setModel(self.model)
#         self.table.setAlternatingRowColors(True)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#         model_index = self.model.index(0, 0)
#         r = self.model.match(model_index, QtCore.Qt.DisplayRole, "463.75", 1, QtCore.Qt.MatchContains)  # type: ignore
#         print(r)
#         self.table.selectionModel().select(r[0], QtCore.QItemSelectionModel.Select)  # type: ignore
#         # self.button = QPushButton("Push me!")
#         v_layout = QVBoxLayout()
#         v_layout.addWidget(self.search_le)
#         v_layout.addWidget(self.table)
#         # v_layout.addWidget(self.button)
#
#         self.setLayout(v_layout)
#         # self.button.clicked.connect(self.magic)
#
#     def search(self, query):
#         if not query:
#             return
#
#         self.model
#
#     def magic(self):
#         # c = self.model.rowCount(QtCore.QModelIndex()) + 1
#         # self.model.insertRow(c, self.model.createIndex(c, 0))
#         # self.model.setData()
#         self.model._data.append(
#             list(
#                 Item(title="Cookie", bar_code="459849584958", price=Decimal("2.55"), quantity=5, owner_id=1, id=100)
#                 .dict(exclude={"id", "owner_id"})
#                 .values()
#             )
#         )


# TODO: move this to utils
def create_widgets_with_layout(layout_type: Type[Union[QVBoxLayout, QHBoxLayout]], *widgets):
    layout = layout_type()
    for widget in widgets:
        layout.addWidget(widget)
    return layout


class EditItem(QWidget):
    def __init__(self, parent, item: Item) -> None:
        super().__init__()

        self.item_id = item.id

        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        # self.save_btn.clicked.connect(self.save_field_changes)

        h_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        self.name_le = QLineEdit(item.title)
        self.barcode_le = QLineEdit(item.bar_code)
        self.price_le = QLineEdit(str(item.price))
        self.quantity_le = QLineEdit(str(item.quantity))
        self.description_te = QTextEdit(item.description)
        self.description_te.setLineWrapMode(QTextEdit.WidgetWidth)

        form_layout = QFormLayout()
        form_layout.addRow("<b>Name:</b>", self.name_le)
        form_layout.addRow("<b>Bar Code:</b>", self.barcode_le)
        form_layout.addRow("<b>Price:</b>", self.price_le)
        form_layout.addRow("<b>Quantity:</b>", self.quantity_le)
        form_layout.addRow("<b>Description:</b>", self.description_te)

        image_path = "broken-image32x32.png" if item.image_path is None else item.image_path
        self.image_lbl = QLabel()
        self.image_lbl.setPixmap(QtGui.QPixmap(image_path))

        h_layout.addWidget(self.image_lbl)
        h_layout.addLayout(form_layout)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(create_widgets_with_layout(QHBoxLayout, self.save_btn, self.cancel_btn))

        self.setLayout(main_layout)
        self.resize(500, 500)
        self.setWindowTitle("Edit")

    def __check_for_empty_qlinedit(self, *qlinedits: QLineEdit):
        return [qlinedit for qlinedit in qlinedits if not qlinedit.text()]

    def save_field_changes(self):
        print("Function 2")
        empty_fields = self.__check_for_empty_qlinedit(self.name_le, self.barcode_le, self.price_le, self.quantity_le)
        print(empty_fields)


# TODO: change the background color when the mouse hover this widget
class ItemView(QWidget):
    clicked = QtCore.Signal(QtCore.QObject)

    def __init__(self, item: Item):
        super().__init__()

        self.item = item

        name_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Name:<\b>"), QLabel(item.title))
        bar_code_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Bar Code:<\b>"), QLabel(item.bar_code))
        price_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Price:<\b>"), QLabel(str(item.price)))
        quantity_layout = create_widgets_with_layout(
            QVBoxLayout, QLabel("<b>Quantity:<\b>"), QLabel(str(item.quantity))
        )

        # self.description = QTextEdit(item.description)
        # self.description.setReadOnly(True)
        # self.description.setLineWrapMode(QTextEdit.WidgetWidth)
        # description_layout = QVBoxLayout()
        # description_layout.addWidget(QLabel("<b>Description:<\b>"))
        # description_layout.addWidget(self.description)

        # TODO: rescale image if its too big
        image_path = "broken-image32x32.png" if item.image_path is None else item.image_path
        image_lbl = QLabel()
        image_lbl.setPixmap(QtGui.QPixmap(image_path))

        container_layout = create_widgets_with_layout(QHBoxLayout, image_lbl)
        container_layout.addLayout(name_layout)
        container_layout.addLayout(bar_code_layout)
        container_layout.addLayout(price_layout)
        container_layout.addLayout(quantity_layout)

        self.setLayout(container_layout)
        self.setAutoFillBackground(True)
        self.p = self.palette()
        self.setPalette(self.p)

    def mousePressEvent(self, _: QtGui.QMouseEvent):
        self.clicked.emit(self)
        # self.p.setColor(QtGui.QPalette.Window, QtCore.Qt.green)

    # def enterEvent(self, event: QtGui.QEnterEvent) -> None:
    #     print(f"Mouse em cima {self.item}")
    #     return super().enterEvent(event)
    #
    # def leaveEvent(self, event: QtCore.QEvent) -> None:
    #     print(f"Mouse fora {self.item}")
    #     return super().leaveEvent(event)


# TODO: store the clicked ItemView and change its background color
class ItemsList(QWidget):
    clicked = QtCore.Signal(QtCore.QObject)
    ended = QtCore.Signal()

    def __init__(self, items: list[Item]):
        super().__init__()

        self._size = 0
        self.widget = QWidget()
        self.scroll_area = QScrollArea()
        self.items_layout = QVBoxLayout()
        self.child_widgets: list[ItemView] = []

        self.scroll_area.setWidgetResizable(True)
        self.widget.setLayout(self.items_layout)

        self.scroll_area.setWidget(self.widget)

        self.scroll_area.verticalScrollBar().valueChanged.connect(self.__has_scroll_reached_end)

        container = QVBoxLayout()
        container.addWidget(self.scroll_area)
        self.setLayout(container)

        self.add_items(items)

    def __len__(self):
        return self._size

    def __has_scroll_reached_end(self, value):
        if value == self.scroll_area.verticalScrollBar().maximum():
            self.ended.emit()

    def add_items(self, items: list[Item]):
        for item in items:
            self.add_item(item)

    def add_item(self, item: Item):
        child = ItemView(item)
        child.clicked.connect(self.__clicked_item)
        self.child_widgets.append(child)

        self.items_layout.addWidget(child)
        self._size += 1

    def __clicked_item(self, widget: ItemView):
        self.clicked.emit(widget)


class MainWindow(QMainWindow):
    MINIMUM_WIDTH = 500
    MINIMUM_HEIGHT = 500

    def __init__(self, api: TimAPI):
        super().__init__()

        self._api = api
        self.items_list = ItemsList(api.items())
        self.items_list.ended.connect(self.__fetch_more_data)
        self.searchbar = QLineEdit()

        self.items_names = [widget.item.title for widget in self.items_list.child_widgets]

        self.items_list.clicked.connect(self.open_edit_window)
        self.searchbar.textChanged.connect(self.search)

        self.completer = QCompleter(self.items_names)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)

        layout = QVBoxLayout()
        layout.addWidget(self.searchbar)
        layout.addWidget(self.items_list)
        #         self.search_le.textChanged.connect(self.search)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setWindowTitle("T.I.M")
        self.setMinimumSize(MainWindow.MINIMUM_WIDTH, MainWindow.MINIMUM_HEIGHT)

        self.setCentralWidget(central_widget)

    def __fetch_more_data(self):
        for item in self._api.items(skip=len(self.items_list) + 100):
            self.items_list.add_item(item)
            self.items_names.append(item.title)

    def open_edit_window(self, item_view: ItemView):
        self.edit_window = EditItem(self, item_view.item)
        self.edit_window.save_btn.clicked.connect(self.save_edit)
        self.edit_window.cancel_btn.clicked.connect(self.edit_window.close)
        self.edit_window.show()

    def save_edit(self):
        print("Function 1")
        title = self.edit_window.name_le.text()
        price = self.edit_window.price_le.text()
        quantity = self.edit_window.quantity_le.text()
        bar_code = self.edit_window.barcode_le.text()
        description = self.edit_window.description_te.toPlainText()

        self._api.update_item(self.edit_window.item_id,
            ItemUpdate(
                title=title, price=Decimal(price), quantity=int(quantity), bar_code=bar_code, description=description
            )
        )

        self.edit_window.close()

    def search(self, query: str):
        for widget in self.items_list.child_widgets:
            if query.lower() in widget.item.title.lower():
                widget.show()
            else:
                widget.hide()
