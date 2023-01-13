from PyQt6.QtWidgets import QPushButton, QSlider
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class Color:
    dark_violet = "#352A50"
    cyber_grape = "#47376C"
    grape = "#6C52A3"
    apricot = "#F8CDB9"
    light_salmon = "#FFAB84"
    coral = "#FF925F"
    tinted_white = "#FBFAFC"


class IconButton(QPushButton): # tooltip style
    def __init__(self, icon: QIcon, tooltip, size=40):
        super().__init__()

        self.setStyleSheet("""
            QPushButton {
                background: %s;
                border-radius: 5px;
            }

            QPushButton:hover {
                background: #8066b7;
            }

            QPushButton:disabled {
                background: #5C468A;
            }
        """ % Color.grape)

        self.setIcon(icon)
        self.setToolTip(tooltip)

        self.setIconSize(QSize(size,size))
        self.setFixedSize(size,size)