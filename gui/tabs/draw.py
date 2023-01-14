from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QColorDialog, QFileDialog, QPushButton, QSpinBox, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QIcon, QFont
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QBuffer

from utils import Color, IconButton

from PIL import Image
from functools import partial

import io

class DrawTab(QWidget):
    def __init__(self):
        super().__init__()

        self.sidebar = Sidebar()
        self.canvas = Canvas()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.sidebar.tools.thickness_spinbox.valueChanged.connect(self.thickness_event)
        self.sidebar.tools.pen_button.clicked.connect(partial(self.tool_event, 0))
        self.sidebar.tools.text_button.clicked.connect(partial(self.tool_event, 1))
        self.sidebar.tools.eraser_button.clicked.connect(partial(self.tool_event, 2))

        self.sidebar.colors.color_picker_button.clicked.connect(self.color_picker_event)

        self.sidebar.file.load_button.clicked.connect(self.load_event)
        self.sidebar.file.save_button.clicked.connect(self.save_event)
        self.sidebar.file.clear_button.clicked.connect(self.clear_event)

        for v in self.sidebar.colors.children():
            if isinstance(v, ColorButton):
                v.clicked.connect(partial(self.color_default_event, v.color))
    
    def load_event(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Image", "gui/captures", "Image files (*.jpg *.png)")

        if fp:
            self.canvas.image = QImage(fp).scaledToHeight(670)
            self.canvas.image_overlay = QImage(self.canvas.image.size(), QImage.Format.Format_ARGB32)
            self.canvas.image_overlay.fill(Qt.GlobalColor.transparent)
            
            self.canvas.setFixedSize(self.canvas.image.size())

            self.canvas.update()

    def clear_event(self):
        self.canvas.image_overlay.image = QImage(self.canvas.image.size(), QImage.Format.Format_ARGB32)
        self.canvas.image_overlay.fill(Qt.GlobalColor.transparent)

        self.canvas.update()

    def save_event(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "gui/drawings", "JPEG(*.jpg);; PNG(*.png)")
        if fp:
            buffer_image = QBuffer()
            buffer_image.open(QBuffer.OpenModeFlag.ReadWrite)
            self.canvas.image.save(buffer_image, "jpg")

            pil_image = Image.open(io.BytesIO(buffer_image.data()))

            buffer_overlay = QBuffer()
            buffer_overlay.open(QBuffer.OpenModeFlag.ReadWrite)
            self.canvas.image_overlay.save(buffer_overlay, "png")

            pil_overlay = Image.open(io.BytesIO(buffer_overlay.data()))

            pil_image.paste(pil_overlay, (0,0), mask=pil_overlay)
            pil_image.save(fp)
            

    def thickness_event(self, i):
        self.canvas.brush_size = i

    def tool_event(self, i):
        self.canvas.mode = i
        
        for v in self.sidebar.tools.children():
            if isinstance(v, IconButton):
                v.setDisabled(False)

        self.sender().setDisabled(True)

    def color_default_event(self, rgb):
        self.canvas.brush_color = QColor(rgb[0], rgb[1], rgb[2])

    def color_picker_event(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.canvas.brush_color = color

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.file = File()
        self.tools = Tools()
        self.colors = Colors()

        self.file_frame = QWidget()

        self.file_frame.layout = QHBoxLayout()
        self.file_frame.layout.addWidget(self.file)
        self.file_frame.layout.addStretch()

        self.file_frame.layout.setContentsMargins(0,0,0,0)
        self.file_frame.setLayout(self.file_frame.layout)

        self.colors_frame = QWidget()

        self.colors_frame.layout = QVBoxLayout()
        self.colors_frame.layout.addStretch()
        self.colors_frame.layout.addWidget(self.colors)

        self.colors_frame.layout.setContentsMargins(0,0,0,0)
        self.colors_frame.setLayout(self.colors_frame.layout)

        self.lower_frame = QWidget()

        self.lower_frame.layout = QHBoxLayout()
        self.lower_frame.layout.addWidget(self.tools)
        self.lower_frame.layout.addWidget(self.colors_frame)
        self.lower_frame.layout.addStretch()

        self.lower_frame.layout.setContentsMargins(0,0,0,0)
        self.lower_frame.layout.setSpacing(10)

        self.lower_frame.setLayout(self.lower_frame.layout)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.file_frame)
        self.layout.addStretch(1)
        self.layout.addWidget(self.lower_frame)

        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)



class File(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.load_button = IconButton(QIcon("gui/assets/icons/load.png"), "Load image")
        self.save_button = IconButton(QIcon("gui/assets/icons/save.png"), "Save canvas")
        self.clear_button = IconButton(QIcon("gui/assets/icons/reload.png"), "Clear canvas")

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.clear_button)

        self.layout.setSpacing(10)

        self.setLayout(self.layout)

class Tools(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.label = QLabel("Size")
        self.thickness_spinbox = QSpinBox()

        self.pen_button = IconButton(QIcon("gui/assets/icons/pen.png"), "Pen")
        self.text_button = IconButton(QIcon("gui/assets/icons/text.png"), "Text")
        self.eraser_button = IconButton(QIcon("gui/assets/icons/eraser.png"), "Eraser")

        self.pen_button.setDisabled(True)

        self.label.setStyleSheet("""
            QLabel {
                font-family: Montserrat;
                font-size: 14px;
                font-weight: 600;
                color: %s;
            }
        """ % Color.tinted_white)

        self.thickness_spinbox.setStyleSheet("""
            QSpinBox {
                background: %s;
                border-radius: 2px;
            }
        """ % Color.tinted_white)

        self.thickness_spinbox.setMinimum(2)
        self.thickness_spinbox.setValue(10)

        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.thickness_spinbox)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.pen_button)
        self.layout.addWidget(self.text_button)
        self.layout.addWidget(self.eraser_button)

        self.layout.setSpacing(10)

        self.setLayout(self.layout)


class Colors(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QWidget {
                background: %s;
                border-radius: 10px;
            }
        """ % Color.cyber_grape)

        self.color_picker_button = IconButton(QIcon("gui/assets/icons/color-picker.png"), "Color picker", 30)
        self.color_default_toggle_button = IconButton(QIcon("gui/assets/icons/arrow-right.png"), "Show/hide default colors", 30)

        self.color_default_toggle_button.clicked.connect(self.color_default_toggle_event)

        self.layout = QGridLayout()

        self.layout.addWidget(ColorButton((255, 255, 255), "White"), 0, 0)
        self.layout.addWidget(ColorButton((192, 192, 192), "Silver"), 0, 1)
        self.layout.addWidget(ColorButton((128, 128, 128), "Gray"), 0, 2)
        self.layout.addWidget(ColorButton((0, 0, 0), "Black"), 0, 3)

        self.layout.addWidget(ColorButton((255, 0, 0), "Red"), 1, 0)
        self.layout.addWidget(ColorButton((128, 0, 0), "Maroon"), 1, 1)
        self.layout.addWidget(ColorButton((255, 255, 0), "Yellow"), 1, 2)
        self.layout.addWidget(ColorButton((128, 128, 0), "Olive"), 1, 3)

        self.layout.addWidget(ColorButton((0, 255, 0), "Lime"), 2, 0)
        self.layout.addWidget(ColorButton((0, 128, 0), "Green"), 2, 1)
        self.layout.addWidget(ColorButton((0, 255, 255), "Aqua"), 2, 2)
        self.layout.addWidget(ColorButton((0, 128, 128), "Teal"), 2, 3)

        self.layout.addWidget(ColorButton((0, 0, 255), "Blue"), 3, 0)
        self.layout.addWidget(ColorButton((0, 0, 128), "Green"), 3, 1)
        self.layout.addWidget(ColorButton((255, 0, 255), "Fuchsia"), 3, 2)
        self.layout.addWidget(ColorButton((128, 0, 128), "Purple"), 3, 3)

        self.layout.addWidget(self.color_picker_button, 2, 4)
        self.layout.addWidget(self.color_default_toggle_button, 3, 4)

        self.setLayout(self.layout)

        self.color_default_toggle_event()

    def color_default_toggle_event(self):
        for v in self.children():
            if isinstance(v, ColorButton):
                v.setHidden(not v.isHidden())

                visible = v.isVisible()

        if visible:
            self.color_default_toggle_button.setIcon(QIcon("gui/assets/icons/arrow-left.png"))
        else:
            self.color_default_toggle_button.setIcon(QIcon("gui/assets/icons/arrow-right.png"))

class ColorButton(QPushButton):
    def __init__(self, rgb, tooltip):
        super().__init__()

        self.color = rgb
        hover_rgb = [v+20 if v+20 <= 255 else v-20 for v in rgb]

        self.setStyleSheet("""
            QPushButton {
                background: rgb(%s, %s, %s);
                border-radius: 5px;
            }

            QPushButton:hover {
                background: rgb(%s, %s, %s);
            }
        """ % (rgb[0], rgb[1], rgb[2], hover_rgb[0], hover_rgb[1], hover_rgb[2]))

        self.setToolTip(tooltip)
        self.setFixedSize(30,30)
    

class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        self.image = QImage(1360, 670, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

        self.image_overlay = QImage(1360, 670, QImage.Format.Format_ARGB32)
        self.image_overlay.fill(Qt.GlobalColor.transparent)

        self.setFixedSize(self.image.size())

        self.mode = 0

        self.brush_size = 10
        self.brush_color = QColor(Color.coral)

        self.last = QPoint()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.mode == 1:
                text, s = QInputDialog.getText(self, "Text", "Text to display")

                if s:
                    painter = QPainter(self.image_overlay)
                    painter.setPen(QPen(self.brush_color))
                    painter.setFont(QFont("Montserrat", self.brush_size+10))

                    painter.drawText(e.position(), text)
                    self.update()
            else:
                self.last = e.position()

    def mouseMoveEvent(self, e):
        painter = QPainter(self.image_overlay)
        painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        if self.mode == 0:
            painter.drawLine(self.last, e.position())
        elif self.mode == 2:
            painter.save()

            painter.setPen(QPen(self.brush_color, self.brush_size+10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.drawLine(self.last, e.position())

            painter.restore()       

        self.last = e.position()
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())
        painter.drawImage(self.rect(), self.image_overlay, self.image.rect())