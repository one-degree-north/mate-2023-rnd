from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QColorDialog, QFileDialog, QPushButton
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QIcon
from PyQt6.QtCore import Qt, QPoint, QRect

from utils import Color, IconButton

class DrawTab(QWidget):
    def __init__(self):
        super().__init__()

        self.draw_bar = DrawBar()
        self.canvas = Canvas()

        self.canvas_frame = QWidget()
        self.canvas_frame.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.canvas_frame.layout = QVBoxLayout()
        self.canvas_frame.layout.addWidget(self.canvas)
        self.canvas_frame.setLayout(self.canvas_frame.layout)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.draw_bar)
        self.layout.addStretch()
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.draw_bar.color_picker_button.clicked.connect(self.color_picker_event)
        self.draw_bar.load_button.clicked.connect(self.set_image)
        self.draw_bar.save_button.clicked.connect(self.save)

    def save(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "gui/drawings", "JPEG(*.jpg);; PNG(*.png)")
        if fp:
            self.canvas.image.save(fp)

    def set_image(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Image", "gui/captures", "Image files (*.jpg *.png)")

        if fp:
            self.canvas.image = QImage(fp).scaledToHeight(680)
            self.canvas.setFixedSize(self.canvas.image.size())

            self.canvas.update()

        # painter = QPainter(self.canvas)
        # painter.drawImage(self.canvas.rect(), self.canvas.image, self.canvas.image.rect())

    def color_picker_event(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.canvas.brush_color = color

# default colors, color selector, pen size, load image, save image, clear, eraser, undo/redo?
# empty canvas (select color)

class DrawBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.color_picker_button = IconButton(QIcon("gui/assets/icons/quit.png"), "Color")
        self.load_button = IconButton(QIcon("gui/assets/icons/settings.png"), "Load")
        self.save_button = IconButton(QIcon("gui/assets/icons/settings.png"), "Load")
        self.a = ColorButton((20,200,20), "Green")

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.color_picker_button)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.save_button)
        self.layout.addStretch()
        self.layout.addWidget(self.a)

        self.layout.setSpacing(10)

        self.setLayout(self.layout)

class ColorButton(QPushButton):
    def __init__(self, rgb, tooltip):
        super().__init__()

        self.setStyleSheet("""
            QToolTip {
                background: %s;
                color: black;
                font-family: Inter;
            }

            QPushButton {
                background: rgb(%s, %s, %s);
                border-radius: 5px;
            }

            QPushButton:hover {
                background: rgb(%s, %s, %s);
            }
        """ % (Color.grape, rgb[0], rgb[1], rgb[2], rgb[0]+10, rgb[1]+10, rgb[2]+10))

        self.setToolTip(tooltip)
        self.setFixedSize(30,30)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        self.image = QImage(1360, 680, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

        self.setFixedSize(self.image.size())

        self.drawing = False

        self.brush_size = 10
        self.brush_color = QColor(Color.coral)

        self.last = QPoint()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.last = e.position()

    def mouseMoveEvent(self, e):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)) #23:00
        painter.drawLine(self.last, e.position())

        self.last = e.position()
        self.update()

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