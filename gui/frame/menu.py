from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

# import cv2

from utils import *

class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-right-radius: 10px;
            }
        """ % Color.cyber_grape)


        self.information = Information()
        self.tab_buttons = TabButtons()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.information)
        self.layout.addWidget(self.tab_buttons)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

class TabButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.quit_button = IconButton(QIcon("gui/assets/icons/test.png"), "Quit")
        self.quit_button.clicked.connect(self.quit_event)

        self.emergency_stop_button = IconButton(QIcon("gui/assets/icons/test.png"), "Emergency stop")#, "#F54242", "#F56A6A")
        self.emergency_stop_button.clicked.connect(self.emergency_stop_event)

        self.settings_button = IconButton(QIcon("gui/assets/icons/test.png"), "Settings tab")
        self.settings_button.clicked.connect(self.settings_event)

        self.camera_button = IconButton(QIcon("gui/assets/icons/test.png"), "Camera tab")
        self.camera_button.clicked.connect(self.camera_event)

        self.visualize_button = IconButton(QIcon("gui/assets/icons/test.png"), "Visualize tab")
        self.visualize_button.clicked.connect(self.visualize_event)

        self.analyze_button = IconButton(QIcon("gui/assets/icons/test.png"), "Analyze tab")
        self.analyze_button.clicked.connect(self.analyze_event)


        self.layout = QGridLayout()

        self.layout.addWidget(self.visualize_button, 0,0)
        self.layout.addWidget(self.analyze_button, 0,1)
        self.layout.addWidget(self.settings_button, 1,0)
        self.layout.addWidget(self.camera_button, 1,1)
        self.layout.addWidget(self.quit_button, 2,0)
        self.layout.addWidget(self.emergency_stop_button, 2,1)

        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(8)

        self.setLayout(self.layout)

    def quit_event(self):
        pass

    def emergency_stop_event(self):
        pass

    def settings_event(self):
        pass

    def camera_event(self):
        pass

    def visualize_event(self):
        pass

    def analyze_event(self):
        pass

class Information(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-right-radius: 10px;
            }
        """ % Color.dark_violet)
        
        
        self.image_frame = QLabel()
        self.image_frame.setStyleSheet("""
            QLabel {
                background: %s;
                margin: 5px;
                padding: 5px;
                border-radius: 10px;
            }
        """ % Color.tinted_white)

        image = QPixmap('gui/assets/images/logo.png')
        self.image_frame.setPixmap(image)

        self.image_frame.setFixedSize(100,100)
        self.image_frame.setScaledContents(True)


        self.title = QLabel("1\u00B0N MATE R&D")
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.title.setStyleSheet("""
            QLabel {
                color: %s;
                font-family: Montserrat;
                font-weight: 700;
            }
        """ % Color.tinted_white)

        self.version = QLabel(f"v0.1") # version
        self.version.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.version.setStyleSheet("""
            QLabel {
                color: %s;
                font-family: Montserrat;
                font-weight: 500;
                font-size: 10px;
            }
        """ % Color.tinted_white)


        self.layout = QVBoxLayout()

        self.layout.addWidget(self.image_frame)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.version)

        self.layout.setSpacing(4)

        self.setLayout(self.layout)