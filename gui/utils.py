from PyQt6.QtWidgets import QPushButton
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
    def __init__(self, icon: QIcon, tooltip, background="#6C52A3", hover="#8066b7"):
        super().__init__()

        self.setStyleSheet("""
            QToolTip {
                background: %s;
            }

            QPushButton {
                background: %s;
                border-radius: 5px;
            }

            QPushButton:hover {
                background: %s;
            }
        """ % (Color.tinted_white, background, hover))

        self.setIcon(icon)
        self.setToolTip(tooltip)

        self.setIconSize(QSize(40,40))
        self.setFixedSize(40,40)

