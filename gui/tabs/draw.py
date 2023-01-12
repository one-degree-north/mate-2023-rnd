from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QColorDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QIcon
from PyQt6.QtCore import Qt, QPoint

from utils import Color, IconButton

class DrawTab(QWidget):
    def __init__(self):
        super().__init__()

        self.draw_bar = DrawBar()
        self.canvas = Canvas()

        self.canvas_frame = QWidget()
        self.canvas_frame.setStyleSheet("background: green; padding: 30px;")
        self.canvas_frame.layout = QVBoxLayout()
        self.canvas_frame.layout.addWidget(self.canvas)
        self.canvas_frame.setLayout(self.canvas_frame.layout)

        self.layout = QHBoxLayout()

        self.layout.addStretch()
        self.layout.addWidget(self.draw_bar)
        self.layout.addWidget(self.canvas)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.draw_bar.color_picker_button.clicked.connect(self.color_picker_event)

    def color_picker_event(self):
        self.canvas.brush_color = QColorDialog.getColor()

class DrawBar(QWidget):
    def __init__(self):
        super().__init__()

        self.color_picker_button = IconButton(QIcon("gui/assets/icons/quit.png"), "Color")

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.color_picker_button)

        self.setLayout(self.layout)

class Canvas(QLabel):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                background: %s;
                border-radius: 10px;
                border: 10px solid black;
            }
        """ % Color.tinted_white)

        self.image = QImage("gui/captures/cam_test.png").scaledToHeight(600)

        self.setFixedSize(self.image.size())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drawing = False

        self.brush_size = 10
        self.brush_color = Qt.GlobalColor.green

        self.last = QPoint()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last = e.position()

    def mouseMoveEvent(self, e):
        if self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)) #23:00
            painter.drawLine(self.last, e.position())

            self.last = e.position()
            self.update()


    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())



    # def paintEvent(self, e):
    #     self.painter = QPainter()
    #     self.painter.begin(self)

    #     # self.painter.drawLine(100, 200, 200, 200)

    #     # self.painter.end()

    # def mousePressEvent(self, e):
    #     if e.button() == Qt.MouseButton.LeftButton:
    #         self.drawing = True
    #         self.last = e.position()
    #         print('a')

    # def mouseReleaseEvent(self, e):
    #     if e.button() == Qt.MouseButton.LeftButton:
    #         self.drawing = False

    

    # def mouseMoveEvent(self, e):
    #     if self.drawing:
    #         painter = QPainter()
    #         painter.begin(self)

    #         painter.setPen(QColor(20, 201, 222))

    #         # painter.drawLine(self.last, e.position())
    #         painter.drawText(e.position(), "ok")

    #         self.last = e.position()

    #         painter.end()


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