from python_qt_binding import loadUi
from PyQt5.Qt import *
from PyQt5.QtGui import *
import os
from rosplane_msgs.msg import Waypoint
from gm_plotter import LatLon

PWD = os.path.dirname(os.path.abspath(__file__))

class WaypointPopup(QWidget):
	def __init__(self, marble_map, waypoint, uifname='waypoint_popup.ui'):
		super(WaypointPopup, self).__init__()
		print('Created waypoint popup')
		ui_file = os.path.join(PWD, 'resources', uifname)
		loadUi(ui_file, self)
		self.marble_map = marble_map
		self.waypoint = waypoint
		self._air_speed.setText(str(self.waypoint.Va_d))
		self._alt.setText(str(self.waypoint.alt))
		self._go_button.clicked.connect(self.go_clicked)
		self._delete_wp.clicked.connect(self.delete_clicked)

	def go_clicked(self):
		self.marble_map.go_to_waypoint(self.waypoint)

	def delete_clicked(self):
		self.marble_map.delete_waypoint(self.waypoint)

