from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon

from gui.utils import IconButton

class Controls(QWidget):
    def __init__(self):
        super().__init__()

        self.lower_button = IconButton(QIcon("gui/assets/icons/down.png"), "Lower", 80, 10)
        self.eee_button = IconButton(QIcon("gui/assets/icons/settings.png"), "eee")

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.lower_button)
        self.layout.addWidget(self.eee_button)
        self.layout.addStretch()

        self.layout.setSpacing(20)
        self.setLayout(self.layout)
