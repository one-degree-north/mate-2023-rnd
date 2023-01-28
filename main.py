from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

from firmware import rov_comms
from gui.rov import MainWindow

import logging
import sys
import os

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

    # comms = rov_comms.RovComms()

    window = MainWindow(0, 0, 0)
    window.show()


    logging.info("One Degree North R&D GUI has launched successfully")
    print("\033[92mOne Degree North R&D GUI has launched successfully\033[0m")

    app.exec()