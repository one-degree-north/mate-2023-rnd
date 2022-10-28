from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

import cv2
from numpy import ndarray

from utils import *

class CameraTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }

        # """ % Color.dark_violet)

        self.cam_width = 320
        self.cam_height = 240

        self.cam_1 = Camera(self, "Front camera", 0) # settings
        self.cam_2 = Camera(self, "Down camera", 1) # settings

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.cam_1)
        self.layout.addWidget(self.cam_2)

        # self.layout.setSpacing(0)

        self.setLayout(self.layout)

    def resizeEvent(self, event):
        self.cam_width, self.cam_height = self.cam_1.width(), self.cam_1.height()

class Camera(QWidget):
    def __init__(self, parent, name, port):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.parent = parent

        self.viewfinder = QLabel()
        self.viewfinder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(self.parent.cam_width, self.parent.cam_height)

        self.thread = VideoThread(0)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.viewfinder)
        self.setLayout(self.layout)


    def close_event(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.viewfinder.setPixmap(qt_img)

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

    def run(self):
        cap = cv2.VideoCapture(self.port)

        while self.running:
            ret, image = cap.read()
            if ret:
                self.change_pixmap_signal.emit(image)
                
        cap.release()
        
    def stop(self):
        self.running = False
        self.wait()
