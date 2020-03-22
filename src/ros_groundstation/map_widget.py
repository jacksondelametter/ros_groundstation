from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget

from .marble_map import MarbleMap
from .op_window import OpWindow
import map_info_parser
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from waypoint_popup import WaypointPopup
from .map_publishers import WaypointPub

PWD = os.path.dirname(os.path.abspath(__file__))

class MapWindow(QWidget):
    def __init__(self, uifname = 'map_widget.ui'):
        super(MapWindow, self).__init__()
        button_icon_file = os.path.join(PWD, 'resources', 'airplane.png')
        ui_file = os.path.join(PWD, 'resources', uifname)
        loadUi(ui_file, self)
        self.setObjectName(uifname)

        self.gps_dict = map_info_parser.get_gps_dict()
        self.blankname = '-- BLANK MAP --'
        self.gps_dict[self.blankname] = [[0.0, 0.0], 18]
        self._marble_map = MarbleMap(self.gps_dict, self.blankname)
        self.verticalLayout.addWidget(self._marble_map)

        self._home_opts.clear()
        keylist = sorted(self.gps_dict, key=self.gps_dict.get)
        self._home_opts.addItems(keylist)
        self._home_opts.setCurrentIndex(keylist.index(map_info_parser.get_default()))
        self._home_opts.currentIndexChanged[str].connect(self._update_home)

        self._gridview_toggle.stateChanged[int].connect(self._marble_map.grid_viewer_toggle)

        self.init_op_window()
        self._recenter.clicked.connect(self._marble_map.recenter)
        self._clear_waypoints.clicked.connect(self.clear_wp_clicked)
        self._find_aircraft.clicked.connect(self.find_aircraft_clicked)
        self.send = True
        self._send_waypoints.clicked.connect(self.start_end_waypoints_clicked)

    def init_op_window(self):
        self.opWindow = OpWindow(self._marble_map)
        self._map_options.clicked.connect(self.open_op_window)

    def open_op_window(self):
        self.opWindow.show()

    def _update_home(self):
        self._marble_map.change_home(self._home_opts.currentText())

    def closeEvent(self, event): # ++++++++++++++
        self.opWindow.close()
        self.wpWindow.close()
        self.cmWindow.close()
        super(MapWindow, self).close()

    def clear_wp_clicked(self):
        self.send = False
        self.start_end_waypoints_clicked()
        self._marble_map.clear_waypoints()

    def find_aircraft_clicked(self):
        self._marble_map.center_on_aircraft()

    def start_end_waypoints_clicked(self):
        if self.send:
            self._marble_map.start_waypoints()
            self._send_waypoints.setText('Stop')
        else:
            self._marble_map.stop_waypoints()
            self._send_waypoints.setText('Send Path')

        self.send = not self.send

    def save_settings(self, plugin_settings, instance_settings):
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        pass
