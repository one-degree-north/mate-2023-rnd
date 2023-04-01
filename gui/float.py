from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from gui.utils import Color
from gui.widgets.console import Console
from gui.frame.menu import Information

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

        # control
        self.control_label = QLabel("Control")

        self.control_label.setStyleSheet("""
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

        # console
        self.console_label = QLabel("Console")

        self.console_label.setStyleSheet("""
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
        self.layout.addWidget(self.control_label)
        self.layout.addWidget(self.console_label)
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)

        self.setFixedWidth(600)





class FloatMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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