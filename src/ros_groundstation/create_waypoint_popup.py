from python_qt_binding import loadUi
from PyQt5.Qt import *
from PyQt5.QtGui import *
import os
from rosplane_msgs.msg import Waypoint
from gm_plotter import LatLon

PWD = os.path.dirname(os.path.abspath(__file__))

class CreateWaypointPopup(QWidget):
	def __init__(self, marble_map, waypoint, uifname='create_waypoint_popup.ui'):
		super(CreateWaypointPopup, self).__init__()
		print('Created waypoint popup')
		ui_file = os.path.join(PWD, 'resources', uifname)
		loadUi(ui_file, self)
		self.marble = marble_map
		self.waypoint = waypoint

	def init_create_waypoint(self):
		self._position_selector.addItem('Append')
		self._create_wp.clicked.connect(self.create_wp_clicked)
		self._delete_wp.hide()

	def init_update_waypoint(self, current_pos, waypoint_count):
		self.current_pos = current_pos
		self._enter_air_speed.setText(str(self.waypoint.Va_d))
		self._enter_alt.setText(str(abs(self.waypoint.w[2])))
		for i in range(waypoint_count):
			self._position_selector.addItem(str(i + 1))
		self._position_selector.setCurrentIndex(current_pos)
		self._create_wp.setText("Update WP")
		self._create_wp.clicked.connect(self.update_wp_clicked)
		self._delete_wp.clicked.connect(self.delete_wp)

	def get_waypoint_params(self):
		try:
			air_speed = float(self._enter_air_speed.text())
			alt = float(self._enter_alt.text()) * -1
			self.waypoint.Va_d = air_speed
			self.waypoint.w[2] = alt
			return True
		except:
			print('Enter legal air speed and/or alt')
			return False

	def update_wp_clicked(self):
		if self.get_waypoint_params() is False:
			return
		changed_index = self._position_selector.currentIndex()
		self.marble.update_wp(self.waypoint, changed_index, self.current_pos)

	def create_wp_clicked(self):
		if self.get_waypoint_params() is False:
			return
		self.marble.create_wp(self.waypoint)

	def delete_wp(self):
		self.marble.delete_wp(self.current_pos)


