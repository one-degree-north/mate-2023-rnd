from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt

from gui.utils import *

class StopwatchMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-bottom-left-radius: 10px;
            }
        """ % Color.dark_violet)


        self.stopwatch = Stopwatch()
        self.controls = Controls()

        self.controls.quickstart_button.clicked.connect(self.quickstart_event)
        self.controls.toggle_button.clicked.connect(self.toggle_event)
        self.controls.reset_button.clicked.connect(self.reset_event)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.stopwatch)
        self.layout.addWidget(self.controls)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)
    
    def quickstart_event(self):
        self.toggle_event()

    def toggle_event(self):
        if self.stopwatch.timer.isActive():
            self.stopwatch.timer.stop()
            self.controls.toggle_button.setToolTip("Resume")
            self.controls.toggle_button.setIcon(QIcon("gui/assets/icons/start.png"))
            # record time in console?
        else:
            self.controls.quickstart_button.setDisabled(True)
            self.stopwatch.timer.start(100)
            self.controls.toggle_button.setToolTip("Pause")
            self.controls.toggle_button.setIcon(QIcon("gui/assets/icons/pause.png"))

    def reset_event(self):
        self.stopwatch.timer.stop()
        self.stopwatch.deci = 0

        self.stopwatch.stopwatch_label.setText("00:00.0")

        self.controls.toggle_button.setToolTip("Start")
        self.controls.toggle_button.setIcon(QIcon("gui/assets/icons/start.png"))

        self.controls.quickstart_button.setDisabled(False)

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()

        self.stopwatch_label = QLabel("00:00.0")
        self.stopwatch_label.setStyleSheet("""
            QLabel {
                color: %s;
                font-family: Montserrat;
                font-weight: 700;
                font-size: 24px;
            }
        """ % Color.tinted_white)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stopwatch_label)
        self.setLayout(self.layout)

        self.deci = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

    def update_time(self):
        self.deci += 1

        self.stopwatch_label.setText(f"{self.deci // 600:02}:{(self.deci // 10) % 60:02}.{self.deci % 10}")


class Controls(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-bottom-left-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.quickstart_button = IconButton(QIcon("gui/assets/icons/quickstart.png"), "Quickstart")
        self.toggle_button = IconButton(QIcon("gui/assets/icons/start.png"), "Start")
        self.reset_button = IconButton(QIcon("gui/assets/icons/reload.png"), "Reset")

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.quickstart_button)

        self.layout.setSpacing(10)

        self.setLayout(self.layout)