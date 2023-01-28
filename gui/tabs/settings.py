from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QPushButton, QCheckBox
from PyQt6.QtCore import Qt

from functools import partial

from utils import Color

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = Tabs()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.tabs, 1)

        self.setLayout(self.layout)


# matplotlib graph
# pid

class Tabs(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QTabWidget:tab-bar {
                top: 0;
                left: 0;
            }

            QTabBar:tab {
                background-color: %s;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #53457A;
            }

        """ % Color.cyber_grape)

        self.ui_settings = UISettings()
        self.location_settings = LocationSettings()
        self.weather_settings = WeatherSettings()

        self.addTab(self.ui_settings, "App Settings")
        self.addTab(self.location_settings, "Location API Settings")
        self.addTab(self.weather_settings, "Weather API Settings")

        self.setTabPosition(QTabWidget.TabPosition.South)
        

class UISettings(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                font-family: Montserrat;
                font-weight: 80px;

                color: white;
            }

            QCheckBox::indicator {
                background: %s;
                border-radius: 4px;

                width: 40px;
                height: 40px;
            }

            QCheckBox::indicator:checked {
                background: %s;
            }
        """ % (Color.tinted_white, Color.light_salmon))

        self.label = QLabel("Hello")
        self.check = QCheckBox()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)


class LocationSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # hi

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class WeatherSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # hi

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)