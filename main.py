cfrom PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

from firmware import pi_comms
from gui.rov import MainWindow

import logging
import sys
import os

if __name__ == "__main__":
    try:
        os.mkdir("gui/captures")
        print("Directory gui/captures has been created")
    except FileExistsError:
        print("Directory gui/captures exists")

    try:
        os.mkdir("gui/captures/images")
        print("Directory gui/captures/images has been created")
    except FileExistsError:
        print("Directory gui/captures/images exists")

    try:
        os.mkdir("gui/captures/videos")
        print("Directory gui/captures/videos has been created")
    except FileExistsError:
        print("Directory gui/captures/videos exists")

    try:
        with open("gui/logs.log", "x") as f:
            print("File gui/logs.log has been created")
    except FileExistsError:
        print("File gui/logs.log exists")
    
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont("gui/assets/fonts/Montserrat/static/Montserrat-Bold.ttf")
    QFontDatabase.addApplicationFont("gui/assets/fonts/Inter/Inter-Regular.ttf")

    comms = None

    if input("Connect comms (y/n)? ") == "y":
        print("Searching for serial...")
        comms = pi_comms.PIClient((input("enter ip: "), 27777))
        print("Serial found")

    window = MainWindow(comms, 1, 2)
    window.show()
    window.showMaximized()


    logging.info("One Degree North R&D GUI has launched successfully")
    print("\033[92mOne Degree North R&D GUI has launched successfully\033[0m")

    app.exec()