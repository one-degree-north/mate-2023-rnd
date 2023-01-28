from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt

from frame import menu, navigation, time, stopwatch
from tabs import camera, draw, settings
from widgets import console

from utils import Color

import logging
import sys
import os

# test

class LowerSection(QWidget):
    def __init__(self):
        super().__init__()

        self.menu = menu.Menu()
        self.navigation = navigation.Navigation()

        self.console = console.Console()
        self.console.hide()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.menu)
        self.layout.addWidget(self.console)
        self.layout.addStretch()
        self.layout.addWidget(self.navigation)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

        self.navigation.widget_buttons.console_button.clicked.connect(self.console_event)


    def console_event(self):
        self.console.setVisible(not self.console.isVisible())


class UpperSection(QWidget):
    def __init__(self):
        super().__init__()

        self.time = time.Time()
        self.stopwatch_menu = stopwatch.StopwatchMenu()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.time)
        self.layout.addStretch()
        self.layout.addWidget(self.stopwatch_menu)

        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)


class Tabs(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QTabWidget:pane {
                background-color: %s;
                border-radius: 10px;

                margin: 30px 20px 20px 20px;

                padding: 10px;
            }
            
            QTabWidget:tab-bar {
                top: 20px;
                left: 20px;
            }

            QTabBar:tab {
                background-color: %s;
                border-radius: 10px;

                font-family: Montserrat;
                font-size: 14px;
                font-weight: 700;
                color: %s;

                margin-right: 10px;
                padding: 10px;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #443766;
            }
        """ % (Color.dark_violet, Color.dark_violet, Color.tinted_white))


        self.camera_tab = camera.CameraTab()
        self.draw_tab = draw.DrawTab()
        self.autonomous_tab = QWidget()
        self.settings_tab = settings.SettingsTab()

        self.addTab(self.camera_tab, QIcon("gui/assets/icons/camera.png"), "Camera")
        self.addTab(self.draw_tab, QIcon("gui/assets/icons/draw.png"), "Draw")
        self.addTab(self.autonomous_tab, QIcon("gui/assets/icons/chart.png"), "Autonomous")
        self.addTab(self.settings_tab, QIcon("gui/assets/icons/settings.png"), "Settings")

        

        





class MainWindow(QMainWindow):
    def __init__(self, cam_port_1, cam_port_2, rov_comms):
        super().__init__()
        self.rov_comms = rov_comms
        self.setWindowTitle("User Interface")
        self.setMinimumSize(800, 600)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    spread: pad, 
                    x1:0 y1:0,
                    x2:0 y2:1,
                    stop:0 %s, 
                    stop:1 %s
                );
            }
        """ % (Color.light_salmon, Color.apricot))

        self.lower_section = LowerSection()
        self.upper_section = UpperSection()
        self.tabs = Tabs()

        # layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.upper_section)
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.lower_section)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        # parent layout
        self.parent = QWidget()
        self.parent.setLayout(self.layout)

        self.setCentralWidget(self.parent)

        self.showMaximized()

        # keyboard input stuff
        self.speed = 10
        self.pid = False

    def keyPressEvent(self, e):
        if self.lower_section.console.command_line.key_logging:
            logging.debug(f"{e.text()} ({e.key()})")
        
        if e.key() == Qt.Key.Key_1:
            pass
        if e.key() == Qt.Key.Key_W:
            self.rov_comms.

    def keyReleaseEvent(self, e):




if __name__ == "__main__":
    try:
        os.mkdir("gui/captures")
        print("gui/captures has been created")
    except FileExistsError:
        print("gui/captures exists")

    try:
        os.mkdir("gui/captures/images")
        print("gui/captures/images has been created")
    except FileExistsError:
        print("gui/captures/images exists")

    try:
        os.mkdir("gui/captures/videos")
        print("gui/captures/videos has been created")
    except FileExistsError:
        print("gui/captures/videos exists")

    try:
        with open("gui/logs.log", "x") as f:
            print("gui/logs.log has been created")
    except FileExistsError:
        print("gui/logs.log exists")
    
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Montserrat/static/Montserrat-Bold.ttf")
    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Inter/Inter-Regular.ttf")

    window = MainWindow(0, 0)
    window.show()

    logging.info("One Degree North R&D GUI has launched successfully")
    print("\033[92mOne Degree North R&D GUI has launched successfully\033[0m")

    app.exec()