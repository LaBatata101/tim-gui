from typing import Type, Union
from PySide6.QtWidgets import QLayoutItem, QVBoxLayout, QHBoxLayout, QWidget

def create_widgets_with_layout(layout_type: Type[Union[QVBoxLayout, QHBoxLayout]], *widgets):
    layout = layout_type()
    for widget in widgets:
        if isinstance(widget, QLayoutItem):
            layout.addItem(widget)
        else:
            layout.addWidget(widget)
    return layout


def center_window(win: QWidget):
    fg = win.frameGeometry()
    center = win.screen().availableGeometry().center()
    fg.moveCenter(center)
    win.move(fg.topLeft())


def check_for_empty_fields(*qlinedits):
    return [qlinedit for qlinedit in qlinedits if not qlinedit.text()]
