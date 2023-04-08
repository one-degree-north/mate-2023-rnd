from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from gui.utils import Color
from gui.sidebar.console import Console
from gui.sidebar.controls import Controls
from gui.sidebar.chart import Chart
from gui.frame.menu import Information

import logging

from random import randint

class Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """ % Color.dark_violet)

        # title
        self.title = QLabel("MATE Float")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title.setStyleSheet("""
            QLabel {
                font-family: Montserrat;
                font-size: 42px;
                font-weight: 700;
                color: %s;

                padding: 20px;
            }
        """ % Color.tinted_white)


        # graph
        self.chart_label = HeaderLabel("Chart")
        self.chart = Chart()


        # control
        self.control_label = HeaderLabel("Control")
        self.controls = Controls()


        # console
        self.console_label = HeaderLabel("Console")
        self.console = Console()

        # layout
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(self.title)

        self.layout.addStretch(1)

        self.layout.addWidget(self.chart_label)
        self.layout.addWidget(self.chart)

        self.layout.addWidget(self.control_label)
        self.layout.addWidget(self.controls)

        self.layout.addWidget(self.console_label)
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)

        self.setFixedWidth(400)

class HeaderLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setStyleSheet("""
            QLabel {
                border-bottom: 10px solid %s;
                border-radius: 0;

                font-family: Montserrat;
                font-size: 24px;
                font-weight: 700;
                color: %s;

                padding: 10px;
                margin: 10px;
            }
        """ % (Color.cyber_grape, Color.tinted_white))

class FloatMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.lower_debouce = False

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
        """ % (Color.pacific_cyan, Color.light_cyan))

        self.panel = Panel()
        self.panel.controls.lower_button.clicked.connect(self.lower_event)

        self.information = Information()

        self.information.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-left-radius: 10px;
            }
        """ % Color.dark_violet)

        self.information_frame = QWidget()
        self.information_frame.layout = QVBoxLayout()
        self.information_frame.layout.addStretch()
        self.information_frame.layout.addWidget(self.information)
        self.information_frame.layout.setContentsMargins(0,0,0,0)
        self.information_frame.setLayout(self.information_frame.layout)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.panel)
        self.layout.addStretch()
        self.layout.addWidget(self.information_frame)

        self.layout.setContentsMargins(0,0,0,0)

        self.parent = QWidget()
        self.parent.setLayout(self.layout)
        self.setCentralWidget(self.parent)

    def update_graph(self, data): # data should be 2d list in order: velocity, angular velocity, accel, angular accel
        self.panel.chart.canvas.data = data
        self.panel.chart.draw_selected()

    def lower_event(self):
        self.lower_debouce = True

        logging.info("Vertical profiling float in progress...")
        # something probably with threading
        logging.info("Vertical profiling float complete!")
        # data show

        data = []
        for i in range(4):
            data.append([randint(1, 100) for _ in range(10)])

        self.update_graph(data)
        
        self.lower_debouce = False