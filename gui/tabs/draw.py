from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt

from utils import Color

class DrawTab(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = Canvas()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        

class Canvas(QLabel):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.tinted_white)

        # self.image =   QLabel()
        self.drawing = False

    def paintEvent(self, e):
        self.painter = QPainter()
        self.painter.begin(self)

        # self.painter.drawLine(100, 200, 200, 200)

        # self.painter.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last = e.position()
            print('a')

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    

    def mouseMoveEvent(self, e):
        if self.drawing:
            painter = QPainter()
            painter.begin(self)
            painter.setPen(QColor(20, 201, 222))

            painter.drawLine(self.last, e.position())

            self.last = e.position()

            painter.end()


    # def paintEvent(self, e):
    #     painter = QPainter(self)
    #     painter.drawImage(self.rect(), self.image, self.image.rect())

    # def paintEvent(self, e):
    #     self.qp = QPainter()
    #     self.qp.begin(self)
        
    #     self.qp.setPen(QColor(100, 100, 200))
    #     # self.qp.drawText(e.rect(), Qt.AlignmentFlag.AlignCenter, "asdijodjasdo")

    #     # self.mouseMoveEvent = self.draw(qp)

    #     # qp.end()



    # def draw(self, e):
    #     # print(e.position().x())
    #     # print(e.position().x(),)
    #     self.qp.drawPoint(e.position().x(), e.position().y())