from pathlib import Path

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLayoutItem, QLineEdit,
                               QPushButton, QScrollArea, QSpacerItem,
                               QVBoxLayout, QWidget)

from tim_gui.api.models import Item, User, UserUpdate
from tim_gui.gui.utils import center_window, create_widgets_with_layout

icons_path = Path(__file__).parent.parent.parent / "icons"


class PreviewImage(QLabel):
    def __init__(self):
        super().__init__()

        self.preview_window = QWidget()
        self.preview_window.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.preview_lbl = QLabel()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.preview_lbl)

        self.preview_window.setLayout(layout)

        center_window(self.preview_window)

    def enterEvent(self, event: QtGui.QEnterEvent):
        preview_image = self.pixmap().scaled(256, 256, mode=QtCore.Qt.SmoothTransformation)

        self.preview_lbl.setPixmap(preview_image)
        self.preview_window.show()

        return super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):
        self.preview_window.close()
        return super().leaveEvent(event)


class ItemView(QWidget):
    clicked = QtCore.Signal(QtCore.QObject)

    def __init__(self, item: Item):
        super().__init__()

        self.item = item
        self.is_selected = False

        self.name_lbl = QLabel(item.title)
        self.barcode_lbl = QLabel(item.bar_code)
        self.price_lbl = QLabel(str(item.price))
        self.quantity_lbl = QLabel(str(item.quantity))

        name_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Name:<\b>"), self.name_lbl)
        bar_code_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Bar Code:<\b>"), self.barcode_lbl)
        price_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Price:<\b>"), self.price_lbl)
        quantity_layout = create_widgets_with_layout(QVBoxLayout, QLabel("<b>Quantity:<\b>"), self.quantity_lbl)

        image_path = f"{icons_path}/broken-image32x32.png" if item.image_path is None else item.image_path
        self.image_lbl = PreviewImage()
        self.set_image(image_path)

        container_layout = create_widgets_with_layout(QHBoxLayout, self.image_lbl)
        container_layout.addLayout(name_layout)
        container_layout.addLayout(bar_code_layout)
        container_layout.addLayout(price_layout)
        container_layout.addLayout(quantity_layout)

        self.setLayout(container_layout)
        self.setAutoFillBackground(True)
        self._palette = self.palette()

    def select(self):
        self.is_selected = True
        self._palette.setColor(QtGui.QPalette.Window, QtCore.Qt.green)
        self.setPalette(self._palette)

    def clear_selection(self):
        self.is_selected = False
        self.setPalette(QtGui.QPalette())

    def mousePressEvent(self, _: QtGui.QMouseEvent):
        self.clicked.emit(self)

    def enterEvent(self, event: QtGui.QEnterEvent):
        if not self.is_selected:
            self._palette.setColor(self.backgroundRole(), QtCore.Qt.darkGray)
            self.setPalette(self._palette)
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):
        if not self.is_selected:
            self.clear_selection()
        super().leaveEvent(event)

    def set_image(self, image_path: str):
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.width() > 64 or pixmap.height() > 64:
            pixmap = pixmap.scaled(64, 64)
        self.image_lbl.setPixmap(pixmap)

    def update(self, item: Item):
        self.item = item

        self.name_lbl.setText(item.title)
        self.price_lbl.setText(str(item.price))
        self.price_lbl.setText(str(item.quantity))
        self.barcode_lbl.setText(item.bar_code)

        if item.image_path is not None:
            self.set_image(item.image_path)


class ListView(QWidget):
    reachedEnd = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.container = QWidget()
        self.scroll_area = QScrollArea()
        self.widgets_layout = QVBoxLayout()

        self.container.setLayout(self.widgets_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container)

        self.scroll_area.verticalScrollBar().valueChanged.connect(self.__has_scroll_reached_end)

        container = QVBoxLayout()
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(self.scroll_area)

        self.setLayout(container)

    def __has_scroll_reached_end(self, value):
        if value == self.scroll_area.verticalScrollBar().maximum():
            self.reachedEnd.emit()

    def addWidget(self, widget: QWidget):
        self.widgets_layout.addWidget(widget)

    def insertWidget(self, index: int, widget: QWidget):
        self.widgets_layout.insertWidget(index, widget)

    def addSpacerItem(self, item: QSpacerItem):
        self.widgets_layout.addSpacerItem(item)

    def takeAt(self, index: int) -> QLayoutItem:
        return self.widgets_layout.takeAt(index)

    def count(self) -> int:
        return self.widgets_layout.count()

    def addStretch(self):
        self.widgets_layout.addStretch()

    def removeWidget(self, widget: QWidget):
        self.widgets_layout.removeWidget(widget)

    def clear(self):
        for i in reversed(range(self.widgets_layout.count())):
            item = self.widgets_layout.itemAt(i)
            if item.spacerItem():
                self.widgets_layout.removeItem(item)
            else:
                item.widget().deleteLater()


class ItemsList(ListView):
    clicked = QtCore.Signal(QtCore.QObject)

    def __init__(self, items: list[Item]):
        super().__init__()

        self.child_widgets: set[ItemView] = set()
        self.selected_widget: ItemView | None = None

        self.add_items(items)

    def __len__(self):
        return self.count()

    def add_items(self, items: list[Item]):
        # remove the Stretch at the end of the layout before inserting new widgets
        child = self.takeAt(self.count() - 1)
        if child is not None and child.spacerItem():
            del child

        for item in items:
            self.add_item(item)

        self.addStretch()

    def insert_item(self, index: int, item: Item):
        child = ItemView(item)
        child.clicked.connect(self.__clicked_item)
        self.child_widgets.add(child)

        self.insertWidget(index, child)

    def add_item(self, item: Item):
        self.insert_item(self.count() - 1, item)

    def remove_selected_item(self):
        if self.selected_widget is not None:
            self.removeWidget(self.selected_widget)
            self.selected_widget.deleteLater()

    def __clicked_item(self, widget: ItemView):
        if self.selected_widget is not None:
            self.selected_widget.clear_selection()

        widget.select()
        self.selected_widget = widget

        self.clicked.emit(widget)


class ClickableLabel(QLabel):
    clicked = QtCore.Signal()

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, _: QtGui.QMouseEvent) -> None:
        self.clicked.emit()


class CustomLineEdit(QWidget):
    def __init__(self, text: str = "", is_required=True) -> None:
        super().__init__()

        v_layout = QVBoxLayout()
        self.le = QLineEdit(text)
        if is_required:
            self.le.textChanged.connect(self.__is_empty)

        self.lbl = QLabel()
        self.lbl.hide()
        self.lbl.setAlignment(QtCore.Qt.AlignTop)
        self.lbl.setStyleSheet("color: red")
        self.lbl.setMargin(0)

        v_layout.addWidget(self.le)
        v_layout.addWidget(self.lbl)
        v_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(v_layout)

    def __is_empty(self, text):
        if text == "":
            self.draw_empty_field_warning()
        else:
            self.le.setStyleSheet("")
            self.lbl.hide()

    def draw_empty_field_warning(self):
        self.le.setStyleSheet("border: 1px solid red")
        self.lbl.setText("Cannot be empty!")
        self.lbl.show()

    def text(self):
        return self.le.text()

    def setEchoMode(self, echo_mode: QLineEdit.EchoMode):
        self.le.setEchoMode(echo_mode)

    def addAction(self, icon, action):
        return self.le.addAction(icon, action)


class PasswordEdit(CustomLineEdit):
    def __init__(self, is_required: bool = True):
        super().__init__(is_required=is_required)

        self.password_shown = False

        self.setEchoMode(QLineEdit.Password)
        self.toggle_password_action = self.addAction(
            QtGui.QIcon(f"{icons_path}/eye_open32x32.png"), QLineEdit.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.on_toggle_password_action)

    def on_toggle_password_action(self):
        if not self.password_shown:
            self.setEchoMode(QLineEdit.Normal)
            self.password_shown = True
            self.toggle_password_action.setIcon(QtGui.QIcon(f"{icons_path}/eye_closed32x32.png"))
        else:
            self.setEchoMode(QLineEdit.Password)
            self.password_shown = False
            self.toggle_password_action.setIcon(QtGui.QIcon(f"{icons_path}/eye_open32x32.png"))


class UserEditItem(QWidget):
    editUser = QtCore.Signal(User)
    deleteUser = QtCore.Signal(User)

    def __init__(self, user: User) -> None:
        super().__init__()

        self._palette = self.palette()

        self.edit_btn = QPushButton()
        self.delete_btn = QPushButton()

        self.edit_btn.setToolTip("Edit user")
        self.delete_btn.setToolTip("Delete user")
        self.edit_btn.setIcon(QtGui.QIcon(f"{icons_path}/edit32x32.png"))
        self.delete_btn.setIcon(QtGui.QIcon(f"{icons_path}/trash32x32.png"))

        self.edit_btn.clicked.connect(lambda: self.editUser.emit(user))
        self.delete_btn.clicked.connect(lambda: self.deleteUser.emit(user))

        self.name_lbl = QLabel(user.name)
        self.email_lbl = QLabel(user.email)
        self.is_admin_lbl = QLabel("Yes" if user.is_admin else "No")

        main_layout = QHBoxLayout()
        main_layout.addLayout(create_widgets_with_layout(QVBoxLayout, QLabel("<b>Name:</b>"), self.name_lbl))
        main_layout.addLayout(create_widgets_with_layout(QVBoxLayout, QLabel("<b>Email:</b>"), self.email_lbl))
        main_layout.addLayout(create_widgets_with_layout(QVBoxLayout, QLabel("<b>Is Admin:</b>"), self.is_admin_lbl))
        main_layout.addLayout(create_widgets_with_layout(QHBoxLayout, self.edit_btn, self.delete_btn))

        self.setLayout(main_layout)
        self.setAutoFillBackground(True)

    def enterEvent(self, event: QtGui.QEnterEvent):
        self._palette.setColor(self.backgroundRole(), QtCore.Qt.darkGray)
        self.setPalette(self._palette)
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent):
        self.setPalette(QtGui.QPalette())
        super().leaveEvent(event)

    def update_item(self, user: UserUpdate):
        if user.name is not None:
            self.name_lbl.setText(user.name)

        if user.email is not None:
            self.email_lbl.setText(user.email)

        if user.is_admin is not None:
            self.is_admin_lbl.setText("Yes" if user.is_admin else "No")
