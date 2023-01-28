from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QPushButton, QSlider
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from functools import partial
from gui.utils import Color

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
                margin-right: 10px;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #53457A;
            }
        """ % Color.cyber_grape)

        self.app_settings = AppSettings()
        self.pid_settings = PIDSettings()
        self.location_settings = LocationSettings()
        self.weather_settings = WeatherSettings()

        self.addTab(self.app_settings, QIcon("gui/assets/icons/app.png"), "App Settings")
        self.addTab(self.pid_settings, "PID Settings")
        self.addTab(self.location_settings, QIcon("gui/assets/icons/location.png"), "Location API Settings")
        self.addTab(self.weather_settings, QIcon("gui/assets/icons/weather.png"), "Weather API Settings")

        self.setTabPosition(QTabWidget.TabPosition.South)
        

class AppSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # hi

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class PIDSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        for i in range(18):
            slider = QSlider(Qt.Orientation.Vertical)

            slider.setStyleSheet("""
                QSlider:groove {
                    background: %s;
                    border-radius: 4px;

                    width: 10px;
                }

                QSlider:handle {
                    background: %s;
                    border-radius: 4px;
                    
                    height: 20px;
                }
            """ % (Color.cyber_grape, Color.tinted_white))


            slider.setRange(0, 300)
            slider.valueChanged.connect(partial(self.slider_updated, i))

            self.layout.addWidget(slider)

        self.layout.addStretch()

        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def slider_updated(self, value, slider_id):
        print(value, slider_id)



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