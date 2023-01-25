from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QDateTime, QThread, pyqtSignal, pyqtSlot

import cv2
from numpy import ndarray

import logging

from utils import *

class CameraTab(QWidget):
    def __init__(self):
        super().__init__()

        self.cam_width = 720
        self.cam_height = 480

        self.cam_1 = CameraFrame(self, "front", 0)
        self.cam_2 = CameraFrame(self, "down", 1)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.cam_1)
        self.layout.addWidget(self.cam_2)

        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def resizeEvent(self, e):
        self.cam_width = (self.cam_1.width() + self.cam_2.width()) / 2
        self.cam_height = (self.cam_1.height() + self.cam_2.height()) / 2


class CameraFrame(QWidget):
    def __init__(self, parent, name, port):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.name = name

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }

            QLabel {
                font-family: Montserrat;
                font-size: 14px;
                color: %s;
            }
        """ % (Color.cyber_grape, Color.tinted_white))

        self.label = QLabel(f"{name.title()} camera - Port {port}")
        self.cam = Camera(parent, port)
        self.control_bar = ControlBar()

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cam, 1)
        self.layout.addWidget(self.control_bar)

        self.setLayout(self.layout)

        self.control_bar.capture_button.clicked.connect(self.capture_event)
        self.control_bar.record_button.clicked.connect(self.record_event)

    def capture_event(self):
        try:
            time = QDateTime.currentDateTime().toString("dd-MM-yyyy@hh-mm-ss.zz")
            fn = f"gui/captures/images/{time}_{self.name}-cam.jpg"

            cv2.imwrite(fn, self.cam.thread.image)
            logging.info(f"Image capture on {self.name.upper()} camera has been saved to {fn}")
            
        except (cv2.error, AttributeError):
            print('error')

    def record_event(self):
        if not self.cam.thread.recording:
            try:
                time = QDateTime.currentDateTime().toString("dd-MM-yyyy@hh-mm-ss.z")
                self.fn = f"gui/captures/videos/{time}_{self.name}-cam.avi"

                self.cam.thread.video_recording = cv2.VideoWriter(self.fn, cv2.VideoWriter_fourcc(*"MJPG"), 30, (self.cam.thread.image.shape[1], self.cam.thread.image.shape[0]))
                
                self.cam.thread.recording = True
                self.control_bar.record_button.setIcon(QIcon("gui/assets/icons/stop.png"))

            except (cv2.error, AttributeError):
                print('error')
        else:
            self.cam.thread.recording = False

            self.cam.thread.video_recording.release()
            logging.info(f"Video capture on {self.name.upper()} camera has been saved to {self.fn}")

            self.control_bar.record_button.setIcon(QIcon("gui/assets/icons/record.png"))

            

class ControlBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                font-size: 24px;
            }
        """)

        self.capture_button = IconButton(QIcon("gui/assets/icons/camera.png"), "Capture")

        self.record_timer = QLabel("00:00")
        self.record_button = IconButton(QIcon("gui/assets/icons/record.png"), "Record")

        self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.capture_button)
        self.layout.addStretch()
        self.layout.addWidget(self.record_timer)
        self.layout.addWidget(self.record_button)

        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class Camera(QLabel):
    def __init__(self, parent, port):
        super().__init__("Connecting...")

        self.parent = parent

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.thread = VideoThread(port)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()


    def close_event(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.parent.cam_width, self.parent.cam_height, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)
    


        
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(ndarray)

    def __init__(self, port):
        super().__init__()

        self.running = True
        self.port = port

        self.recording = False

    def run(self):
        cap = cv2.VideoCapture(self.port)

        while self.running:
            ret, self.image = cap.read()
            if ret:
                self.change_pixmap_signal.emit(self.image)

                if self.recording:
                    self.video_recording.write(self.image)
                
        cap.release()
        
    def stop(self):
        self.running = False
        self.wait()