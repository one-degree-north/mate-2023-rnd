from gui.utils import Color
from gui.widgets.console import Console

class Console(Console):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QPlainTextEdit, QLineEdit {
                font-family: Inter;
                font-size: 14px;
                color: %s;
            }
        """ % Color.tinted_white)

        self.command_line.setStyleSheet("""
            QLineEdit {
                background: %s;

                padding: 10px;
                margin: 5px;
                
                border-radius: 8px;
            }
        """ % Color.cyber_grape)