from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox

from gui.utils import Color

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from functools import partial

matplotlib.use("QtAgg")

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