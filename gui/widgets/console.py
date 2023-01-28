from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel, QDialog, QLineEdit
from PyQt6.QtCore import Qt

import logging

from gui.utils import Color

class Console(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }

            QPlainTextEdit, QLineEdit {
                font-family: Inter;
                color: %s;
            }
        """ % (Color.dark_violet, Color.tinted_white))

        self.layout = QVBoxLayout()

        self.logs = Logs()
        self.command_line = CommandLine()

        self.layout.addWidget(self.logs)
        self.layout.addWidget(self.command_line)

        # self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)

class Logs(QDialog, QPlainTextEdit, logging.Handler):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QScrollBar {
                width: 10px;
            }

            QScrollBar:sub-page, QScrollBar:add-page {
                background: %s;
            }

            QScrollBar:sub-page {
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }

            QScrollBar:add-page {
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
            }

            QScrollBar:sub-line, QScrollBar:add-line {
                width: 0;
            }

            QScrollBar:handle {
                background: %s;

                border-radius: 4px;
            }
        """ % (Color.cyber_grape, Color.grape))

        self.logger = QPlainTextEdit()
        self.logger.setReadOnly(True)

        fh = logging.FileHandler("gui/logs.log", mode="a", encoding="utf-8")

        logging.getLogger().setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)

        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "[%H:%M:%S]"))
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "[%d/%m/%y] [%H:%M:%S]"))

        logging.getLogger().addHandler(self)
        logging.getLogger().addHandler(fh)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.logger)

        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)
        
    def reject(self):
        pass

    def emit(self, record):
        msg = self.format(record)
        self.logger.appendPlainText(msg)

class CommandLine(QLineEdit):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLineEdit {
                background: %s;

                border-radius: 4px;
            }
        """ % Color.cyber_grape)

        self.setPlaceholderText('"help" for commands')

        self.returnPressed.connect(self.command_event)

        self.key_logging = False
    
    def command_event(self):
        command, *msg = self.text().split(" ")
        self.clear()

        if command == "help":
            if len(msg) == 0 or msg[0] not in ["help", "return", "key"]:
                logging.info("""
                Help Menu
                ↪ help
                ↪ return
                ↪ key

                () ⭢ required
                [] ⭢ optional
                + ⭢ at least one arg""")

            elif msg[0] == "help":
                logging.info("""
                help
                ↪ shows the help menu
                """)

            elif msg[0] == "return":
                logging.info("""
                return (args+)
                ↪ prints out information to the console
                """)

            elif msg[0] == "key":
                logging.info("""
                key
                ↪ toggles key logging
                """)

        elif command == "return":
            if len(msg) > 0:
                logging.info(" ".join(msg))
            else:
                logging.error("Not enough arguments provided")

        elif command == "key":
            self.key_logging = not self.key_logging
            logging.info(f"Key logging has been set to {str(self.key_logging).upper()}")

        else:
            logging.error(f'Command "{command}" does not exist')