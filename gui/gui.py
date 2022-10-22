from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QFontDatabase

from frame import menu, navigation
import tabs
import widgets

from utils import Color

import sys
import os

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


class MainWindow(QMainWindow):
    def __init__(self, cam_port_1, cam_port_2):
        super().__init__()

        self.setWindowTitle("User Interface")

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

        # layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.upper_section,)
        self.layout.addStretch(1)
        self.layout.addWidget(self.lower_section)

        self.layout.setContentsMargins(0,0,0,0)

        # parent layout
        self.parent = QWidget()
        self.parent.setLayout(self.layout)

        self.setCentralWidget(self.parent)




if __name__ == "__main__":
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Montserrat/Montserrat-VariableFont_wght.ttf")
    QFontDatabase.addApplicationFont(f"{os.path.dirname(__file__)}/assets/fonts/Inter/Inter-VariableFont_slnt,wght.ttf")

    window = MainWindow(0, 1)
    window.show()

    app.exec()