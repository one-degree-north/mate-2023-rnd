from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

from gui.utils import Color, IconButton
from gui.widgets.console import Console
from gui.frame.menu import Information

import logging
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from functools import partial

from random import randint

matplotlib.use("QtAgg")

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

        # field
        self.lower_button = IconButton(QIcon("gui/assets/icons/down.png"), "Lower", 80, 10)

        self.controls = QWidget()

        self.controls.layout = QHBoxLayout()

        self.controls.layout.addWidget(self.lower_button)
        self.controls.layout.addWidget(IconButton(QIcon("gui/assets/icons/settings.png"), "eee"))
        self.controls.layout.addStretch()


        self.controls.layout.setSpacing(20)
        self.controls.setLayout(self.controls.layout)


        # console
        self.console_label = HeaderLabel("Console")

        self.console = Console()

        self.console.setStyleSheet("""
            QPlainTextEdit, QLineEdit {
                font-family: Inter;
                font-size: 14px;
                color: %s;
            }
        """ % Color.tinted_white)

        self.console.command_line.setStyleSheet("""
            QLineEdit {
                background: %s;

                padding: 10px;
                margin: 5px;
                
                border-radius: 8px;
            }
        """ % Color.cyber_grape)

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

class Chart(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = Canvas()
        self.checkboxes = CheckBoxes(self)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.checkboxes)

        self.setLayout(self.layout)

    def draw_selected(self):
        self.canvas.draw_selected(self.checkboxes.selected)


class CheckBoxes(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.velo_check = CheckBox("Velocity")
        self.velo_check.stateChanged.connect(partial(self.checked, 0))

        self.ang_velo_check = CheckBox("Angular Velocity")
        self.ang_velo_check.stateChanged.connect(partial(self.checked, 1))

        self.acc_check = CheckBox("Accel")
        self.acc_check.stateChanged.connect(partial(self.checked, 2))

        self.ang_acc_check = CheckBox("Angular Accel")
        self.ang_acc_check.stateChanged.connect(partial(self.checked, 3))

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.velo_check)
        self.layout.addWidget(self.ang_velo_check)
        self.layout.addWidget(self.acc_check)
        self.layout.addWidget(self.ang_acc_check)

        self.setLayout(self.layout)

        self.selected = [False] * 4

    def checked(self, i):
        self.selected[i] = not self.selected[i]
        self.parent.draw_selected()

class CheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__(text)

        self.setStyleSheet("""
            QCheckBox {
                font-family: Montserrat;
                font-size: 12px;
                font-weight: 700;
                color: %s;
            }
        """ % Color.tinted_white)

class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure(figsize=(3, 3), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

        self.all_lines = ("V (m/s)", "AV (rad/s)", "A (m/s\u00b2)", "AA (rad/s\u00b2)")

        self.data = [[]] * 4 # velo, ang velo, acc, ang acc


    def draw_selected(self, selected):
        self.axes.cla()
        lines = []
        
        for i, v in enumerate(selected):
            if v:
                self.axes.plot(list(range(len(self.data[i]))), self.data[i])
                lines.append(self.all_lines[i])
        self.axes.legend([])
        self.axes.legend(lines)
        self.draw()

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
        self.panel.lower_button.clicked.connect(self.lower_event)

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