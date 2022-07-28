from decimal import Decimal
from pathlib import Path

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (QCheckBox, QDoubleSpinBox, QFileDialog,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QMessageBox, QPushButton,
                               QSizePolicy, QSpacerItem, QSpinBox, QTextEdit,
                               QVBoxLayout, QWidget)

from tim_gui.api import TimAPI
from tim_gui.api.models import (ItemCreate, ItemUpdate, User, UserCreate,
                                UserUpdate)
from tim_gui.gui.custom_widgets import (ClickableLabel, CustomLineEdit,
                                        ItemsList, ItemView, ListView,
                                        PasswordEdit, UserEditItem)
from tim_gui.gui.utils import (center_window, check_for_empty_fields,
                               create_widgets_with_layout)

icons_path = Path(__file__).parent.parent.parent / "icons"


class LoginWindow(QWidget):
    def __init__(self, api: TimAPI, width: int = 350, height: int = 350):
        super().__init__()

        self.api = api

        self.setWindowTitle("T.I.M - Login")
        self.setFixedSize(width, height)

        self.login_lbl = QLabel("<b>Login:</b>")
        self.password_lbl = QLabel("<b>Password:</b>")

        self.login_lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.password_lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.login_le = QLineEdit()
        self.password_le = PasswordEdit()

        self.signin_btn = QPushButton("Sign in")
        self.signin_btn.clicked.connect(self.signin)

        v_layout = create_widgets_with_layout(
            QVBoxLayout,
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding),
            self.login_lbl,
            self.login_le,
            self.password_lbl,
            self.password_le,
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding),
            self.signin_btn,
        )
        self.setLayout(v_layout)

    def signin(self):
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

        self.main_window = MainWindow(self.api)
        self.main_window.showMaximized()


class CreateItemWindow(QWidget):
    itemCreated = QtCore.Signal(ItemCreate)

    def __init__(self, api: TimAPI):
        super().__init__()

        self._api = api

        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        self.save_btn.setIcon(QtGui.QIcon(f"{icons_path}/tick32x32.png"))
        self.cancel_btn.setIcon(QtGui.QIcon(f"{icons_path}/close32x32.png"))

        self.save_btn.clicked.connect(self.create_item)

        h_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        self.name_le = CustomLineEdit()
        self.barcode_le = CustomLineEdit()
        self.price_sb = QDoubleSpinBox()
        self.quantity_sb = QSpinBox()
        self.description_te = QTextEdit()
        self.description_te.setLineWrapMode(QTextEdit.WidgetWidth)

        self.price_sb.setRange(0.0, 2_147_483_647)
        self.price_sb.setValue(0)

        self.quantity_sb.setRange(0, 2_147_483_647)
        self.quantity_sb.setValue(0)

        form_layout = QFormLayout()
        form_layout.addRow("<b>Name:</b>", self.name_le)
        form_layout.addRow("<b>Bar Code:</b>", self.barcode_le)
        form_layout.addRow("<b>Price:</b>", self.price_sb)
        form_layout.addRow("<b>Quantity:</b>", self.quantity_sb)
        form_layout.addRow("<b>Description:</b>", self.description_te)

        self.image_lbl = ClickableLabel()
        self.image_lbl.setPixmap(QtGui.QPixmap(f"{icons_path}/broken-image32x32.png"))
        self.image_lbl.setAlignment(QtCore.Qt.AlignTop)
        self.image_lbl.clicked.connect(self.__set_image)

        h_layout.addWidget(self.image_lbl)
        h_layout.addLayout(form_layout)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(create_widgets_with_layout(QHBoxLayout, self.save_btn, self.cancel_btn))

        self.setLayout(main_layout)
        self.resize(500, 500)
        self.setWindowTitle("Create Item")
        center_window(self)

    def __set_image(self):
        dialog = QFileDialog.getOpenFileName(self, "Open File", filter="Image files (*.jpg *.png)")
        image_path = dialog[0]
        if image_path:
            self.image_lbl.setPixmap(QtGui.QPixmap(image_path).scaled(128, 128))

    def create_item(self):
        empty_fields = check_for_empty_fields(self.name_le, self.barcode_le)
        if empty_fields:
            for empty_field in empty_fields:
                if isinstance(empty_field, CustomLineEdit):
                    empty_field.draw_empty_field_warning()
            return

        title = self.name_le.text()
        price = self.price_sb.text().replace(",", ".")
        quantity = self.quantity_sb.value()
        bar_code = self.barcode_le.text()
        description = self.description_te.toPlainText()

        item = ItemCreate(
            title=title, price=Decimal(price), quantity=quantity, bar_code=bar_code, description=description
        )
        self._api.create_item(
            self._api.get_user_me().id,
            item,
        )

        self.itemCreated.emit(item)

        self.close()


class EditItemWindow(QWidget):
    aboutToClose = QtCore.Signal()
    itemDeleted = QtCore.Signal()

    def __init__(self, item_view: ItemView, api: TimAPI) -> None:
        super().__init__()

        item = item_view.item
        self.item_view = item_view
        self.item_id = item.id
        self._api = api

        self.delete_btn = QPushButton("Delete")
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        self.save_btn.setIcon(QtGui.QIcon(f"{icons_path}/tick32x32.png"))
        self.cancel_btn.setIcon(QtGui.QIcon(f"{icons_path}/close32x32.png"))
        self.delete_btn.setIcon(QtGui.QIcon(f"{icons_path}/trash32x32.png"))
        self.delete_btn.setStyleSheet("color: red")

        self.save_btn.clicked.connect(self.save_edit)
        self.cancel_btn.clicked.connect(self.close)
        self.delete_btn.clicked.connect(self.delete_item)

        h_layout = QHBoxLayout()
        main_layout = QVBoxLayout()

        self.image_path = item.image_path

        self.name_le = CustomLineEdit(item.title)
        self.barcode_le = CustomLineEdit(item.bar_code)
        self.price_sb = QDoubleSpinBox()
        self.quantity_sb = QSpinBox()
        self.description_te = QTextEdit(item.description)
        self.description_te.setLineWrapMode(QTextEdit.WidgetWidth)

        self.price_sb.setRange(0.0, 2_147_483_647)
        self.price_sb.setValue(float(item.price))

        self.quantity_sb.setRange(0, 2_147_483_647)
        self.quantity_sb.setValue(item.quantity)

        form_layout = QFormLayout()
        form_layout.addRow("<b>Name:</b>", self.name_le)
        form_layout.addRow("<b>Bar Code:</b>", self.barcode_le)
        form_layout.addRow("<b>Price:</b>", self.price_sb)
        form_layout.addRow("<b>Quantity:</b>", self.quantity_sb)
        form_layout.addRow("<b>Description:</b>", self.description_te)

        image_path = f"{icons_path}/broken-image32x32.png" if item.image_path is None else item.image_path
        self.image_lbl = ClickableLabel()
        self.image_lbl.setToolTip("Select image...")
        self.image_lbl.setPixmap(QtGui.QPixmap(image_path))
        self.image_lbl.setAlignment(QtCore.Qt.AlignTop)
        self.image_lbl.clicked.connect(self.__set_image)

        h_layout.addWidget(self.image_lbl)
        h_layout.addLayout(form_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Maximum)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(
            create_widgets_with_layout(QHBoxLayout, self.delete_btn, spacer, self.save_btn, self.cancel_btn)
        )

        self.setLayout(main_layout)
        self.resize(500, 500)
        self.setWindowTitle(f"Edit - {item.title}")
        self.setFixedSize(self.size())
        center_window(self)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.aboutToClose.emit()
        super().closeEvent(event)

    def __set_image(self):
        dialog = QFileDialog.getOpenFileName(self, "Open File", filter="Image files (*.jpg *.png)")
        self.image_path = dialog[0]
        if self.image_path:
            self.image_lbl.setPixmap(QtGui.QPixmap(self.image_path).scaled(128, 128))

    def delete_item(self):
        button = QMessageBox.warning(self, "Delete item", "Confirm deletion?", QMessageBox.No, QMessageBox.Yes)

        if button == QMessageBox.Yes:
            self._api.delete_item(self.item_id)
            self.close()
            self.itemDeleted.emit()

    def save_edit(self):
        empty_fields = check_for_empty_fields(self.name_le, self.barcode_le)
        if empty_fields:
            return

        title = self.name_le.text()
        price = self.price_sb.text().replace(",", ".")
        quantity = self.quantity_sb.value()
        bar_code = self.barcode_le.text()
        description = self.description_te.toPlainText()

        item_updated = self._api.update_item(
            self.item_id,
            ItemUpdate(
                title=title,
                price=Decimal(price),
                quantity=quantity,
                bar_code=bar_code,
                description=description,
                image_path=self.image_path,
            ),
        )

        self.item_view.update(item_updated)

        self.close()


class CreateUserWindow(QWidget):
    userCreated = QtCore.Signal()

    def __init__(self, api: TimAPI):
        super().__init__()

        self._api = api

        self.create_btn = QPushButton("Create")
        self.cancel_btn = QPushButton("Cancel")

        self.create_btn.setIcon(QtGui.QIcon(f"{icons_path}/tick32x32.png"))
        self.cancel_btn.setIcon(QtGui.QIcon(f"{icons_path}/close32x32.png"))

        self.create_btn.clicked.connect(self.__create_user)
        self.cancel_btn.clicked.connect(self.close)

        self.name_le = CustomLineEdit()
        self.email_le = CustomLineEdit()
        self.password_le = PasswordEdit()
        self.is_admin_cb = QCheckBox()

        form_layout = QFormLayout()
        form_layout.addRow("<b>Name:</b>", self.name_le)
        form_layout.addRow("<b>Email:</b>", self.email_le)
        form_layout.addRow("<b>Password:</b>", self.password_le)
        form_layout.addRow("<b>Is Admin:</b>", self.is_admin_cb)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(
            create_widgets_with_layout(
                QHBoxLayout,
                self.create_btn,
                self.cancel_btn,
            )
        )

        self.resize(500, 200)
        self.setLayout(main_layout)
        self.setFixedSize(self.size())
        self.setWindowTitle("Create New User")

    def __create_user(self):
        empty_fields = check_for_empty_fields(self.name_le, self.email_le, self.password_le)
        if empty_fields:
            return

        self._api.create_user(
            UserCreate(
                name=self.name_le.text(),
                email=self.email_le.text(),
                is_admin=self.is_admin_cb.isChecked(),
                password=self.password_le.text(),
            )
        )

        self.userCreated.emit()
        self.close()


class BasicUserEditWindow(QWidget):
    userUpdated = QtCore.Signal()

    def __init__(self, api: TimAPI, user: User, width: int = 500, height: int = 500):
        super().__init__()

        self._api = api
        self.current_user = user

        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.is_admin_cb = QCheckBox()
        self.is_admin_cb.setChecked(self.current_user.is_admin)

        self.cancel_btn.clicked.connect(self.close)
        self.save_btn.clicked.connect(self.__update_user)

        self.save_btn.setIcon(QtGui.QIcon(f"{icons_path}/tick32x32.png"))
        self.cancel_btn.setIcon(QtGui.QIcon(f"{icons_path}/close32x32.png"))

        self.name_le = CustomLineEdit(self.current_user.name)
        self.email_le = CustomLineEdit(self.current_user.email)
        self.password_le = PasswordEdit(is_required=False)
        self.password_le.setToolTip("Redefine password")

        self._form_layout = QFormLayout()
        self._form_layout.addRow("<b>Name:</b>", self.name_le)
        self._form_layout.addRow("<b>Email:</b>", self.email_le)
        self._form_layout.addRow("<b>New Password:</b>", self.password_le)
        self._form_layout.addRow("<b>Is Admin:</b>", self.is_admin_cb)

        self._buttons_layout = create_widgets_with_layout(
            QHBoxLayout,
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Maximum),
            self.save_btn,
            self.cancel_btn,
        )

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._form_layout)
        self._main_layout.addLayout(self._buttons_layout)

        self.resize(width, height)
        self.setLayout(self._main_layout)
        self.setFixedSize(self.size())
        self.setWindowTitle(f"Edit User - {self.current_user.name}")

        center_window(self)

    def __update_user(self):
        if check_for_empty_fields(self.name_le, self.email_le):
            return

        name = self.name_le.text()
        email = self.email_le.text()
        password = self.password_le.text()
        is_admin = self.current_user.is_admin
        if not self.is_admin_cb.isHidden():
            is_admin = self.is_admin_cb.isChecked()
        if not password:
            password = None

        # only update if some field changes
        if (
            self.current_user.name != name
            or self.current_user.email != email
            or self.current_user.is_admin != is_admin
            or password
        ):
            self._api.update_user(
                self.current_user.id, UserUpdate(name=name, email=email, password=password, is_admin=is_admin)
            )

        self.userUpdated.emit()
        self.close()


class AdminUserEditWindow(BasicUserEditWindow):
    def __init__(self, api: TimAPI, user: User):
        super().__init__(api, user)

        # Hide the "Is Admin:" label and it's checkbox
        self._form_layout.itemAt(6).widget().hide()
        self.is_admin_cb.hide()

        self.list_view = ListView()
        self._main_layout.insertWidget(1, QLabel("<b>All users:</b>"))
        self._main_layout.insertWidget(2, self.list_view)

        self.create_user_btn = QPushButton("Create User")
        self.create_user_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self._buttons_layout.insertWidget(0, self.create_user_btn)

        self.create_user_btn.clicked.connect(self.__open_create_user_window)

        self.create_user_btn.setIcon(QtGui.QIcon(f"{icons_path}/plus32x32.png"))

        self.populate_user_list()

    def populate_user_list(self):
        for user in self._api.get_users():
            if user.id == self.current_user.id:
                continue

            user_edit = UserEditItem(user)
            user_edit.editUser.connect(self.__edit_user)
            user_edit.deleteUser.connect(self.__delete_user)
            self.list_view.addWidget(user_edit)

        self.list_view.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Maximum, QSizePolicy.Expanding))

    def __edit_user(self, user: User):
        self._edit_user_window = BasicUserEditWindow(self._api, user, height=200)
        self._edit_user_window.userUpdated.connect(self.__update_user_list)
        self._edit_user_window.show()

    def __delete_user(self, user: User):
        button = QMessageBox.warning(
            self, f'Delete user "{user.name}"?', "Confirm deletion?", QMessageBox.No, QMessageBox.Yes
        )

        if button == QMessageBox.Yes:
            self._api.delete_user(user.id)
            self.__update_user_list()

    def __open_create_user_window(self):
        self._create_user_window = CreateUserWindow(self._api)
        self._create_user_window.userCreated.connect(self.__update_user_list)
        self._create_user_window.show()

    # TODO: maybe avoid a request to the api when updating the list
    def __update_user_list(self):
        self.list_view.clear()
        self.populate_user_list()


class NormalUserEditWindow(BasicUserEditWindow):
    def __init__(self, api: TimAPI, user: User):
        super().__init__(api, user, height=200)

        # Hide the "Is Admin:" label and it's checkbox
        self._form_layout.itemAt(6).widget().hide()
        self.is_admin_cb.hide()


class MainWindow(QMainWindow):
    MINIMUM_WIDTH = 500
    MINIMUM_HEIGHT = 500

    def __init__(self, api: TimAPI):
        super().__init__()

        self._api = api
        self.items_list = ItemsList(api.items())
        self.items_list.reachedEnd.connect(self.__fetch_more_data)
        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Search...")

        self.items_list.clicked.connect(self.open_edit_window)
        self.searchbar.textChanged.connect(self.search)

        self.create_new_item_btn = QPushButton("Add new Item")
        self.create_new_item_btn.setIcon(QtGui.QIcon(f"{icons_path}/plus32x32.png"))
        self.create_new_item_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.create_new_item_btn.clicked.connect(self.open_create_window)

        self.config_user_btn = QPushButton()
        self.config_user_btn.setIcon(QtGui.QIcon(f"{icons_path}/gear32x32.png"))
        self.config_user_btn.setToolTip("Edit user")
        self.config_user_btn.clicked.connect(self.__open_edit_user_window)

        central_widget = QWidget()
        central_widget.setLayout(
            create_widgets_with_layout(
                QVBoxLayout,
                self.searchbar,
                self.items_list,
                create_widgets_with_layout(
                    QHBoxLayout,
                    self.create_new_item_btn,
                    QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Maximum),
                    self.config_user_btn,
                ),
            ),
        )

        self.setWindowTitle("T.I.M")
        self.setMinimumSize(MainWindow.MINIMUM_WIDTH, MainWindow.MINIMUM_HEIGHT)

        self.setCentralWidget(central_widget)

    def __fetch_more_data(self):
        print(f"adding more items, current len: {len(self.items_list)}")
        self.items_list.add_items(self._api.items(skip=len(self.items_list) + 100))

    def open_edit_window(self, item_view: ItemView):
        self.edit_window = EditItemWindow(item_view, self._api)
        self.edit_window.aboutToClose.connect(lambda: item_view.clear_selection())
        self.edit_window.itemDeleted.connect(lambda: self.items_list.remove_selected_item())
        self.edit_window.show()

    def open_create_window(self):
        self.create_window = CreateItemWindow(self._api)
        self.create_window.itemCreated.connect(lambda item: self.items_list.insert_item(0, item))
        self.create_window.show()

    def __open_edit_user_window(self):
        user = self._api.get_user_me()  # TODO: avoid a request to the api here
        if user.is_admin:
            self.edit_user_window = AdminUserEditWindow(self._api, user)
        else:
            self.edit_user_window = NormalUserEditWindow(self._api, user)

        self.edit_user_window.show()

    def search(self, query: str):
        # For some reason when searching the scroll moves to the end, thus, fetching more data,
        # this prevents it from happening
        self.items_list.scroll_area.verticalScrollBar().setValue(0)

        for widget in self.items_list.child_widgets:
            if query.lower() in widget.item.title.lower():
                widget.show()
            else:
                widget.hide()
