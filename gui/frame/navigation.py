# include map, compass, and buttons

from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

from utils import *

import io

# import folium # requirements.txt

class Navigation(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-left-radius: 10px;
            }
        """ % Color.cyber_grape)


        self.compass = Compass()
        self.widget_buttons = WidgetButtons()
        self.map = Map()

        self.sublayout = QWidget()
        self.sublayout.layout = QVBoxLayout()

        self.sublayout.layout.addWidget(self.compass)
        self.sublayout.layout.addWidget(self.widget_buttons)

        self.sublayout.layout.setContentsMargins(0,0,0,0)

        self.sublayout.setLayout(self.sublayout.layout)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.sublayout)
        self.layout.addWidget(self.map)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout) ###### setlayout right after = qhboxlayout?

class Map(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-left-radius: 10px;
            }
        """ % Color.dark_violet)

        # self.coordinate = (1.29289, 103.79201)

        self.map_frame = QLabel()
        # self.map_frame.setStyleSheet("""
        #     QLabel {
        #         background: %s;
        #         border-radius: 5px;
        #     }
        # """ % Color.tinted_white)

        image = QPixmap('gui/assets/saved-data/map.png')
        self.map_frame.setPixmap(image)

        self.map_frame.setFixedSize(140,140)
        self.map_frame.setScaledContents(True)

        self.map_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.map_frame)
        self.setLayout(self.layout)

    def update(self):
        pass


class Compass(QWidget):
    def __init__(self):
        super().__init__()


class WidgetButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.weather_button = IconButton(QIcon("gui/assets/icons/weather.png"), "Weather widget")
        self.weather_button.clicked.connect(self.simulation_event)

        self.console_button = IconButton(QIcon("gui/assets/icons/console.png"), "Console widget")
        self.console_button.clicked.connect(self.console_event)


        self.layout = QHBoxLayout()

        self.layout.addWidget(self.console_button)
        self.layout.addWidget(self.weather_button)

        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(8)

        self.setLayout(self.layout)

    def simulation_event(self):
        pass

    def console_event(self):
        pass