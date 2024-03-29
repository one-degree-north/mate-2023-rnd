from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt

from gui.frame import menu, navigation, time, stopwatch
from gui.tabs import camera, draw, settings
from gui.widgets import console

from gui.utils import Color

from functools import partial

import logging
import sys
import os

# test

class LowerSection(QWidget):
    def __init__(self):
        super().__init__()

        self.menu = menu.Menu()
        self.navigation = navigation.Navigation()

        self.console = console.Console()
        self.console.hide()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.menu)
        self.layout.addWidget(self.console)
        self.layout.addStretch()
        self.layout.addWidget(self.navigation)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

        self.navigation.widget_buttons.console_button.clicked.connect(self.console_event)


    def console_event(self):
        self.console.setVisible(not self.console.isVisible())

# orientation, acell, gyro, 

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
            QTabWidget:pane {
                background-color: %s;
                border-radius: 10px;

                margin: 30px 20px 20px 20px;

                padding: 10px;
            }
            
            QTabWidget:tab-bar {
                top: 20px;
                left: 20px;
            }

            QTabBar:tab {
                background-color: %s;
                border-radius: 10px;

                font-family: Montserrat;
                font-size: 14px;
                font-weight: 700;
                color: %s;

                margin-right: 10px;
                padding: 10px;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #443766;
            }
        """ % (Color.dark_violet, Color.dark_violet, Color.tinted_white))


        self.camera_tab = camera.CameraTab()
        self.draw_tab = draw.DrawTab()
        self.autonomous_tab = QWidget()
        self.settings_tab = settings.Tabs()

        self.addTab(self.camera_tab, QIcon("gui/assets/icons/camera.png"), "Camera")
        self.addTab(self.draw_tab, QIcon("gui/assets/icons/draw.png"), "Draw")
        self.addTab(self.autonomous_tab, QIcon("gui/assets/icons/chart.png"), "Autonomous")
        self.addTab(self.settings_tab, QIcon("gui/assets/icons/settings.png"), "Settings")



class MainWindow(QMainWindow):
    def __init__(self, rov_comms, cam_port_1, cam_port_2):
        super().__init__()
        self.rov_comms = rov_comms
        self.setWindowTitle("User Interface")
        self.setMinimumSize(800, 600)

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

        # keyboard input stuff
        self.speed = 0.2
        self.pid = False
        self.pid_angle = False  # angle or gyro for pid
        self.target_thrust = [0, 0, 0, 0, 0, 0]
        self.target_orientation = [0, 0, 0]
        self.claw_open = False
        self.up_thrust_adjustments = [0, 0, 0, 0]

        if self.rov_comms:
            logging.info("Comms have been connected to the GUI")

        for i, v in enumerate(self.tabs.settings_tab.manual_adjustment_settings.children()):
            if isinstance(v, settings.Slider):
                v.valueChanged.connect(partial(self.slider_updated, i))

    def slider_updated(self, value, slider_id):
        print(value, slider_id)
        self.up_thrust_adjustments[slider_id] = value

    def keyPressEvent(self, e):
        # if self.lower_section.console.command_line.key_logging:
        #     logging.debug(f"{e.text()} ({e.key()})")

        if self.rov_comms and not e.isAutoRepeat():
            if e.key() == Qt.Key.Key_1:
                self.speed = 0
            if e.key() == Qt.Key.Key_2:
                self.speed = 0.1
            if e.key() == Qt.Key.Key_3:
                self.speed = 0.2
            if e.key() == Qt.Key.Key_4:
                self.speed = 0.3
            if e.key() == Qt.Key.Key_5:
                self.speed += 0.1
            if e.key() == Qt.Key.Key_6:
                self.speed -= 0.1
            if e.key() == Qt.Key.Key_W:
                self.target_thrust[0] = 1
            if e.key() == Qt.Key.Key_D:
                self.target_thrust[1] = 1
            if e.key() == Qt.Key.Key_A:
                self.target_thrust[1] = -1
            if e.key() == Qt.Key.Key_S:
                self.target_thrust[0] = -1
            if e.key() == Qt.Key.Key_I:
                self.target_thrust[2] = 1
            if e.key() == Qt.Key.Key_K:
                self.target_thrust[2] = -1
            if e.key() == Qt.Key.Key_O:
                if self.pid and self.pid_angle:
                    self.target_thrust[3] += 5
                else:
                    self.target_thrust[3] = 1
            if e.key() == Qt.Key.Key_U:
                if self.pid and self.pid_angle:
                    self.target_thrust[3] -= 5
                else:
                    self.target_thrust[3] = -1
            if e.key() == Qt.Key.Key_Q:
                if self.pi and self.pid_angle:
                    self.target_thrust[4] -= 5
                else:
                    self.target_thrust[4] = -1
            if e.key() == Qt.Key.Key_E:
                if self.pid and self.pid_angle:
                    self.target_thrust[4] += 5
                else:
                    self.target_thrust[4] = 1
            if e.key() == Qt.Key.Key_J:
                if self.pid and self.pid_angle:
                    self.target_thrust[5] -= 5
                else:
                    self.target_thrust[5] = -1
            if e.key() == Qt.Key.Key_L:
                if self.pid and self.pid_angle:
                    self.target_thrust[5] += 5
                else:
                    self.target_thrust[5] = 1
            if e.key() == Qt.Key.Key_BracketRight:  # turn pid on
                self.pid = True
                self.target_thrust = [0, 0, 0, 0, 0, 0]
                print(f"pid on")
            if e.key() == Qt.Key.Key_BracketLeft:   # turn pid off
                self.pid = False
                self.target_thrust = [0, 0, 0, 0, 0, 0]
                print(f"pid off")
            if e.key() == Qt.Key.Key_QuoteLeft: # set gyro pid
                self.pid_angle = False
                print(f"gyro pid on")
            if e.key() == Qt.Key.Key_Semicolon: # set angle pid
                self.pid_angle = True
                print(f"angle pid on")
            if e.key() == Qt.Key.Key_T:
                self.rov_comms.turn_flashlight_on()
            if e.key() == Qt.Key.Key_Y:
                self.rov_comms.turn_flashlight_off()
            if e.key() == Qt.Key.Key_R:
                if self.claw_open:
                    print("closing claw")
                    self.rov_comms.move_claw(0, 2000)
                    self.claw_open = False
                else:
                    print("opening claws")
                    self.rov_comms.move_claw(0, 1000)
                    self.claw_open = True
            if self.pid:
                # turn values into target orientations
                temp_thrust = [0, 0, 0, 0, 0, 0]
                # translation stuff
                for i in range(3):
                    temp_thrust[i] = self.target_thrust[i] * self.speed / 500
                # rotation stuff
                if self.pid_angle:
                    for i in range(3):
                        temp_thrust[i+3] = self.target_thrust[i+3] % 360
                        if temp_thrust[i+3] > 180:
                            temp_thrust[i+3] = temp_thrust[i+3] - 360
                        elif temp_thrust[i+3] < -180:
                            temp_thrust[i+3] = 360 + temp_thrust[i+3]
                else:
                    for i in range(3):
                        temp_thrust[i] = self.target_thrust[i] * self.speed / 500
                print("self thrust: ")
                print(self.target_thrust)
                print("pid thrust: ")
                print(temp_thrust)
                print("orientation: ")
                print(self.rov_comms.orientation)
                self.rov_comms.set_pos_pid(temp_thrust[0:3])
                if self.pid_angle:
                    self.rov_comms.set_rot_angle(temp_thrust[3:6])
                else:
                    self.rov_comms.set_rot_vel(temp_thrust[3:6])
                # self.rov_comms.set_accelerations_thrust(temp_thrust)
            else:
                temp_thrust = [0, 0, 0, 0, 0, 0]
                for i in range(6):
                    temp_thrust[i] = self.target_thrust[i]* self.speed
                print("manual thurst: ")
                print(temp_thrust)
                print(f"up thrust adjustments {self.up_thrust_adjustments}")
                self.rov_comms.set_manual_thrust(temp_thrust)

    def keyReleaseEvent(self, e):
        if self.rov_comms and not e.isAutoRepeat():
            if e.key() == Qt.Key.Key_W:
                self.target_thrust[0] = 0
            if e.key() == Qt.Key.Key_D:
                self.target_thrust[1] = 0
            if e.key() == Qt.Key.Key_A:
                self.target_thrust[1] = 0
            if e.key() == Qt.Key.Key_S:
                self.target_thrust[0] = 0
            if e.key() == Qt.Key.Key_I:
                self.target_thrust[2] = 0
            if e.key() == Qt.Key.Key_K:
                self.target_thrust[2] = 0
            if e.key() == Qt.Key.Key_O:
                if not self.pid:
                    self.target_thrust[3] = 0
            if e.key() == Qt.Key.Key_U:
                if not self.pid:
                    self.target_thrust[3] = 0
            if e.key() == Qt.Key.Key_Q:
                if not self.pid:
                    self.target_thrust[4] = 0
            if e.key() == Qt.Key.Key_E:
                if not self.pid:
                    self.target_thrust[4] = 0
            if e.key() == Qt.Key.Key_J:
                if not self.pid:
                    self.target_thrust[5] = 0
            if e.key() == Qt.Key.Key_L:
                if not self.pid:
                    self.target_thrust[5] = 0
            # if e.key() == Qt.Key.Key_BracketRight:
            #     self.pid = True
            #     self.target_thrust = [0, 0, 0, 0, 0, 0]
            # if e.key() == Qt.Key.Key_BracketLeft:
            #     self.pid = False
            #     self.target_thrust = [0, 0, 0, 0, 0, 0]
            if self.pid:
                # turn values into target orientations
                temp_thrust = [0, 0, 0, 0, 0, 0]
                # translation stuff
                for i in range(3):
                    temp_thrust[i] = self.target_thrust[i] * self.speed / 500
                # rotation stuff
                if self.pid_angle:
                    for i in range(3):
                        temp_thrust[i+3] = self.target_thrust[i+3] % 360
                        if temp_thrust[i+3] > 180:
                            temp_thrust[i+3] = temp_thrust[i+3] - 360
                        elif temp_thrust[i+3] < -180:
                            temp_thrust[i+3] = 360 + temp_thrust[i+3]
                else:
                    for i in range(3):
                        temp_thrust[i] = self.target_thrust[i] * self.speed / 500
                print("self thrust: ")
                print(self.target_thrust)
                print("pid thrust: ")
                print(temp_thrust)
                print("orientation: ")
                print(self.rov_comms.orientation)
                self.rov_comms.set_pos_pid(temp_thrust[0:3])
                if self.pid_angle:
                    self.rov_comms.set_rot_angle(temp_thrust[3:6])
                else:
                    self.rov_comms.set_rot_vel(temp_thrust[3:6])
                # self.rov_comms.set_accelerations_thrust(temp_thrust)
            else:
                temp_thrust = [0, 0, 0, 0, 0, 0]
                for i in range(6):
                    temp_thrust[i] = self.target_thrust[i]* self.speed
                print("manual thurst: ")
                print(temp_thrust)
                print(f"up thrust adjustments {self.up_thrust_adjustments}")
                self.rov_comms.set_manual_thrust(temp_thrust)



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

    window = MainWindow(" ok", 0, 0)
    window.show()

    logging.info("One Degree North R&D GUI has launched successfully")
    print("\033[92mOne Degree North R&D GUI has launched successfully\033[0m")

    app.exec()