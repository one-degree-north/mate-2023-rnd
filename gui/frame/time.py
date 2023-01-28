from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime

from gui.utils import Color

class Time(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-bottom-right-radius: 10px;
            }
        """ % Color.dark_violet)

        self.timer_label = QLabel("00:00")

        self.timer_label.setStyleSheet("""
            QLabel {
                color: %s;
                font-family: Montserrat;
                font-weight: 700;
                font-size: 24px;
            }
        """ % Color.tinted_white)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.timer_label)

        self.setLayout(self.layout)

    def update_time(self):
        time = QTime.currentTime()

        self.timer_label.setText(time.toString("hh:mm A")) # ' or " ??