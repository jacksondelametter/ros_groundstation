from python_qt_binding import loadUi
from PyQt5.Qt import *
from PyQt5.QtGui import *
import os
from rosplane_msgs.msg import Waypoint
from gm_plotter import LatLon

PWD = os.path.dirname(os.path.abspath(__file__))

class CreateWaypointPopup(QWidget):
	def __init__(self, marble_map, wp_latlon, uifname='create_waypoint_popup.ui'):
		super(CreateWaypointPopup, self).__init__()
		print('Created waypoint popup')
		ui_file = os.path.join(PWD, 'resources', uifname)
		loadUi(ui_file, self)
		self.marble = marble_map
		self.wp_latlon = wp_latlon
		self._create_wp.clicked.connect(self.create_wp_clicked)

	def create_wp_clicked(self):
		try:
			air_speed = float(self._enter_air_speed.text())
			alt = float(self._enter_alt.text())
		except:
			print('Enter legal air speed and/or alt')
			return
		self.marble.create_wp(self.wp_latlon, air_speed, alt)
