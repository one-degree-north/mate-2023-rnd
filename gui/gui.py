from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt

from frame import menu, navigation, time, stopwatch
from tabs import camera
import widgets

from utils import Color

import sys
import os

# test

class LowerSection(QWidget):
    def __init__(self):
        super().__init__()

        self.menu = menu.Menu()
        self.navigation = navigation.Navigation()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.menu)
        self.layout.addStretch()
        self.layout.addWidget(self.navigation)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)

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
            QTabWidget::pane {
                background-color: %s;
                border-radius: 10px;

                margin: 30px 20px 20px 20px;

                padding: 10px;
            }

            
            QTabWidget::tab-bar {
                top: 20px;
                left: 20px;
            }

            QTabBar::tab {
                background-color: %s;
                border-radius: 10px;

                font-family: Montserrat;
                font-size: 14px;
                font-weight: 700;
                color: %s;

                margin-right: 10px;
                padding: 10px;
            }

            QTabBar::tab::selected, QTabBar::tab::hover {
                background-color: #443766;
            }
        """ % (Color.dark_violet, Color.dark_violet, Color.tinted_white))


        self.settings_tab = QWidget()
        self.camera_tab = camera.CameraTab()
        self.chart_tab = QWidget()
        self.draw_tab = QWidget()

        self.addTab(self.settings_tab, "Settings")
        self.addTab(self.camera_tab, "Camera")
        self.addTab(self.chart_tab, "Chart")
        self.addTab(self.draw_tab, "Draw")



class MainWindow(QMainWindow):
    def __init__(self, cam_port_1, cam_port_2):
        super().__init__()

        self.setWindowTitle("User Interface")
        # self.setMinimumWidth(800)

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

        # tab

        # self.tab_layout = QWidget()
        # self.tab_layout.layout = QVBoxLayout()
        # self.tab_layout.layout.addWidget(self.tabs)
        # self.tab_layout.setLayout(self.tab_layout.layout)

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




if __name__ == "__main__":
    app = QApplication(sys.argv)

    # app.setStyle("Breeze")

    # os.system('sass gui/style-sheet/scss/main.scss gui/style-sheet/css/main.css') # compile sass

    # with open('gui/style-sheet/css/main.css', 'r') as f:
    #     app.setStyleSheet(f.read())

    print(f"{os.path.dirname(__file__)}/assets/fonts/Montserrat/Montserrat-VariableFont_wght.ttf")

    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Montserrat/static/Montserrat-Bold.ttf")
    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Inter/Inter-Regular.ttf")
    # x = QFont("Montserrat")
    # QFont.setHintingPreference(x, QFont.HintingPreference.PreferNoHinting)

    window = MainWindow(0, 0)
    window.show()
    # window.sethint


    app.exec()