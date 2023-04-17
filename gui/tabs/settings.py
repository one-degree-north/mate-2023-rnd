from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QSlider, QLabel, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

from functools import partial
from gui.utils import Color, IconButton

# from pygrabber.dshow_graph import FilterGraph

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = Tabs()

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.tabs, 1)

        self.setLayout(self.layout)


# matplotlib graph
# pid

class Tabs(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QTabWidget:tab-bar {
                top: -20px;
                left: 20px;
            }

            QTabBar:tab {
                background-color: %s;
                margin-right: 20px;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #53457A;
            }

            QTabWidget:pane {
                margin: 20px;
            }
        """ % Color.cyber_grape)

        self.app_settings = AppSettings()
        self.location_settings = LocationSettings()
        self.weather_settings = WeatherSettings()
        self.pid_settings = PIDSettings()
        self.manual_adjustment_settings = ManualAdjustmentSettings()

        self.addTab(self.app_settings, QIcon("gui/assets/icons/app.png"), "App Settings")
        self.addTab(self.location_settings, QIcon("gui/assets/icons/location.png"), "Location Settings")
        self.addTab(self.weather_settings, QIcon("gui/assets/icons/weather.png"), "Weather Settings")
        self.addTab(self.pid_settings, QIcon("gui/assets/icons/pid.png"), "PID Settings")
        self.addTab(self.manual_adjustment_settings, QIcon("gui/assets/icons/pid.png"), "I Don't Know Manual Adjustment Settings")

        self.setTabPosition(QTabWidget.TabPosition.South)
        

class AppSettings(QWidget):
    def __init__(self):
        super().__init__()

        # I REMOVED CAMERA SETTINGS SINCE IT USES WINDOWS EXCLUSIVE SHIT THAT I CAN'T TEST WITH
        self.camera_header = Header("Camera Ports")

        self.front_camera_setting = Setting("Front camera", CameraSelection())
        self.down_camera_setting = Setting("Down camera", CameraSelection())

        self.other_header = Header("Other")
        self.units_setting = Setting("Units", QLabel())

        self.layout = QGridLayout()

        self.layout.addWidget(self.camera_header, 0, 0)
        self.layout.addWidget(self.front_camera_setting, 1, 0)
        self.layout.addWidget(self.down_camera_setting, 2, 0)

        self.layout.addWidget(self.other_header, 0, 1)
        self.layout.addWidget(self.units_setting, 1, 1)

        self.layout.setRowStretch(3, 1)
        self.layout.setColumnStretch(2, 1)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(100)

        self.setLayout(self.layout)

class LocationSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.ipify_header = Header("Ipify API")
        self.ip_setting = Setting("IP", QLabel("8.8.8.8"))
        self.lat_setting = Setting("Latitude", QLabel())
        self.long_setting = Setting("Longitude", QLabel())
        self.country_setting = Setting("Country", QLabel())
        self.state_setting = Setting("State", QLabel())
        self.city_setting = Setting("City", QLabel())
        self.timezone_setting = Setting("Timezone", QLabel())
        self.utc_offset_setting = Setting("UTC Offset", QLabel())
        self.ipify_key_setting = Setting("API Key", QLabel())

        self.geoapify_header = Header("Geoapify API")

        self.map_frame = QLabel()

        image = QPixmap('gui/assets/saved-data/map.png')

        self.map_frame.setPixmap(image)

        self.map_frame.setFixedSize(400, 400)
        self.map_frame.setScaledContents(True)

        self.zoom_setting = Setting("Zoom", QLabel())
        self.geoapify_key_setting = Setting("API Key", QLabel())


        self.layout = QGridLayout()

        self.layout.addWidget(self.ipify_header, 0, 0)
        self.layout.addWidget(self.ip_setting, 1, 0)
        self.layout.addWidget(self.lat_setting, 2, 0)
        self.layout.addWidget(self.long_setting, 3, 0)
        self.layout.addWidget(self.country_setting, 4, 0)
        self.layout.addWidget(self.state_setting, 5, 0)
        self.layout.addWidget(self.city_setting, 6, 0)
        self.layout.addWidget(self.timezone_setting, 7, 0)
        self.layout.addWidget(self.utc_offset_setting, 8, 0)
        self.layout.addWidget(self.ipify_key_setting, 9, 0)


        self.layout.addWidget(self.geoapify_header, 0, 1)
        self.layout.addWidget(self.map_frame, 1, 1, 8, 1)
        self.layout.addWidget(self.zoom_setting, 9, 1)
        self.layout.addWidget(self.geoapify_key_setting, 10, 1)

        self.layout.setRowStretch(11, 1)
        self.layout.setColumnStretch(2, 1)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(100)

        self.setLayout(self.layout)


class WeatherSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # hi

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class PIDSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.pid_sliders = PIDSliders()


        self.layout = QHBoxLayout()

        self.layout.addWidget(self.pid_sliders)
        self.layout.addStretch()

        self.setLayout(self.layout)


class ManualAdjustmentSettings(QWidget):
    def __init__(self):
        super().__init__()



        self.layout = QHBoxLayout()


        for i in range(4):
            slider = Slider(Color.tinted_white)

            slider.setRange(-30, 30)

            self.layout.addWidget(slider)

        self.layout.addStretch()

        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def slider_updated(self, value, slider_id):
        print(value, slider_id)
        


class CameraSelection(QComboBox):
    def __init__(self):
        super().__init__()

        # devices = FilterGraph().get_input_devices()

        # for port, name in enumerate(devices):
        #     self.addItem(f"{port}: {name}")

        
        
class Header(QWidget):
    def __init__(self, text):
        super().__init__()

        self.header = QLabel(text)

        self.setStyleSheet("""
            QLabel {
                font-family: Montserrat;
                font-size: 24px;

                color: %s;
            }
        """ % Color.tinted_white)

        self.update_button = IconButton(QIcon("gui/assets/icons/reload.png"), "Update", 35)

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.update_button)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class Setting(QWidget):
    def __init__(self, text, box):
        super().__init__()

        self.label = QLabel(text)

        self.box = box
        self.box.setFixedHeight(26)

        self.box.setObjectName("box")

        color = Color.cyber_grape
        if not isinstance(self.box, QLabel):
            color = Color.tinted_white

        self.setStyleSheet("""
            QLabel {
                font-family: Inter;
                font-size: 18px;

                color: %s;
            }

            #box {
                font-size: 16px;

                background: %s;
                border-radius: 4px;

                padding: 4px;
            }
        """ % (Color.tinted_white, color))

        self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.layout.addWidget(self.box)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

class PIDSliders(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        for i in range(18):
            match i//6:
                case 0:
                    color = Color.tinted_white
                case 1:
                    color = Color.apricot
                case 2:
                    color = Color.coral

            slider = Slider(color)

            slider.setRange(0, 300)
            slider.valueChanged.connect(partial(self.slider_updated, i))

            self.layout.addWidget(slider)

        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def slider_updated(self, value, slider_id):
        print(value, slider_id)


class Slider(QSlider):
    def __init__(self, color):
        super().__init__()

        self.setStyleSheet("""
                QSlider:groove {
                    background: %s;
                    border-radius: 4px;

                    width: 12px;
                }

                QSlider:handle {
                    background: %s;
                    border-radius: 4px;
                    
                    height: 20px;
                }
            """ % (Color.cyber_grape, color))
