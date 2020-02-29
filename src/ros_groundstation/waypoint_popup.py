from python_qt_binding import loadUi
from PyQt5.Qt import *
from PyQt5.QtGui import *
import os

PWD = os.path.dirname(os.path.abspath(__file__))

class WaypointPopup(QWidget):
	def __init__(self, uifname='waypoint_popup.ui'):
		super(WaypointPopup, self).__init__()
		print('Created waypoint popup')
		ui_file = os.path.join(PWD, 'resources', uifname)
		loadUi(ui_file, self)