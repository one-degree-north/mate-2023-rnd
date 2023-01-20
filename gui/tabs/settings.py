from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QPushButton, QCheckBox
from PyQt6.QtCore import Qt

from utils import Color

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        self.sidebar = Sidebar()
        self.tabs = Tabs()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.sidebar

    def tab_clicked(self, i):
        self.tabs.setCurrentIndex(i)


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.setFixedWidth(300)

class TabButton(QPushButton):
    def __init__(self):
        super().__init__()

        

class Tabs(QTabWidget):
    def __init__(self):
        super().__init__()

        self.ui_settings = UISettings()
        self.location_settings = LocationSettings()
        self.weather_settings = WeatherSettings()

        self.addTab(self.ui_settings, "")
        

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


class APISettings(QWidget):
    def __init__(self):
        super().__init__()

        self.location_settings = LocationSettings()
        self.weather_settings = WeatherSettings()

        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.location_settings)
        self.layout.addWidget(self.weather_settings)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class LocationSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 20px;
            }
        """ % Color.cyber_grape)

class WeatherSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 20px;
            }
        """ % Color.cyber_grape)
