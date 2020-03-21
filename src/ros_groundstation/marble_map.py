from .gm_plotter import GoogleMapPlotter
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget
from PyQt5.QtCore import *
from PyQt5.QtGui import *
QString = type("")
import os.path
from math import sin, cos, radians, asin, sqrt

import map_info_parser
from Signals import WP_Handler
from .Geo import Geobase
from .map_subscribers import *
import os
from gm_plotter import LatLon
from create_waypoint_popup import CreateWaypointPopup
from waypoint_popup import WaypointPopup
from rosplane_msgs.msg import Waypoint, State
from map_subscribers import StateSub
from op_window import OpWindow
from .map_publishers import *
import time

PWD = os.path.dirname(os.path.abspath(__file__))

class MarbleMap(QWidget):
    def __init__(self, gps_dict, blankname, parent=None):
        super(MarbleMap, self).__init__() # QWidget constructor
        self.WPH = WP_Handler()
        self.setCursor(QCursor(Qt.CrossCursor))

        self.waypoint_radius = 25
        self.waypoints = []
        self.dragging_wp = False

        self._gps_dict = gps_dict
        self.blankname = blankname
        self.get_size()
        self.GMP = None
        self.change_home(map_info_parser.get_default())

        self.GB = Geobase(self.latlon[0], self.latlon[1]) # For full current path drawer
        self._mouse_attentive = False
        #self._mouse_attentive = True
        self.movement_offset = QPoint(0,0)

        self.mouse_event_counter = 0
        self.counter_limit = 4
        self.lon_multiplier = -0.25
        self.lat_multiplier = -0.25
        self.wheel_angle = 0
        self.wheel_angle_thresh = 1*120

        # geometric items for drawing
        self.plane_h = 30 # pixels
        self.plane_w = 25 # pixels

        self.draw_gridlines = False
        self.grid_dist = 20 # meters


    def change_home(self, map_name):
        self._home_map = map_name
        self.latlon = self._gps_dict[self._home_map][0]
        self.latlonalt = [self.latlon[0], self.latlon[1], 0.0] # FOR INTERFACING WITH SUBSCRIBERS
        if not InitSub.with_init:
            InitSub.updateInitLatLonAlt(self.latlonalt)
        self.zoom = self._gps_dict[self._home_map][1]
        self.GB = Geobase(self.latlon[0], self.latlon[1])
        if self.GMP is None:
            self.GMP = GoogleMapPlotter(self._gps_dict, self.w_width, self.w_height, self._home_map, self.blankname)
        else:
            self.GMP.UpdateMap(map_name)
        self.update()
        self.WPH.emit_home_change(self._home_map)

    def get_size(self):
        frame_size = self.frameSize()
        self.w_width = frame_size.width()
        self.w_height = frame_size.height()

    def resizeEvent(self, QResizeEvent):
        self.get_size()
        self.GMP.UpdateSize(self.w_width, self.w_height)

    def wheelEvent(self, QWheelEvent):
        self.wheel_angle += QWheelEvent.angleDelta().y()
        if self.wheel_angle >= self.wheel_angle_thresh:
            self.GMP.UpdateZoom(1)
            self.wheel_angle = 0
        if self.wheel_angle <= -self.wheel_angle_thresh:
            self.GMP.UpdateZoom(-1)
            self.wheel_angle = 0

    def mouseMoveEvent(self, QMouseEvent):
        if self.dragging_wp:
            moved_wp = self.initialize_wp(QMouseEvent.pos())
            self.waypoints[self.dragging_wp_index] = moved_wp
        elif not self._mouse_attentive: # we won't do anything with movement in point-and-click mode
            if QMouseEvent.buttons(): # in act of dragging
                self.mouse_event_counter += 1
                if self.mouse_event_counter > self.counter_limit:
                    qpoint_delta = QMouseEvent.pos() - self.movement_offset
                    delta_x = self.lon_multiplier * qpoint_delta.x()
                    lon_incremented = GoogleMapPlotter.pix_to_rel_lon(self.GMP.center.lon, delta_x, self.GMP.zoom)
                    delta_y = self.lat_multiplier * qpoint_delta.y()
                    lat_incremented = GoogleMapPlotter.pix_to_rel_lat(self.GMP.center.lat, delta_y, self.GMP.zoom)
                    self.GMP.UpdateView(lat_incremented, lon_incremented)
                    #print('InitialLat', self.latlon[0], 'initial lon', self.latlon[1])
                    self.mouse_event_counter = 0

    def recenter(self):
        self.GMP.UpdateView(self.latlon[0], self.latlon[1])

    def center_on_aircraft(self):
        self.GMP.UpdateView(StateSub.lat, StateSub.lon)

    def enterEvent(self, QEvent):
        if self._mouse_attentive:
            self.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def leaveEvent(self, QEvent):
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, QMouseEvent):
        mouse_click = QMouseEvent.pos()
        wp_tuple = self.clicked_on_waypoint(mouse_click)
        if QMouseEvent.button() == Qt.RightButton and wp_tuple is not None:
            print("Clicked on waypoint")
            self.wp_popup = CreateWaypointPopup(self, wp_tuple[1])
            self.wp_popup.init_update_waypoint(wp_tuple[0], len(self.waypoints))
            self.wp_popup.show()
        elif QMouseEvent.button() == Qt.RightButton:
            #StateSub.injectState()
            waypoint = self.initialize_wp(mouse_click)
            #self.waypoints.append(LatLon(lat, lon))
            #print('lat: ', lat, " lon: ", lon)
            self.show_waypoint_popup(waypoint)
        elif QMouseEvent.button() == Qt.LeftButton and wp_tuple is not None:
            self.dragging_wp = True
            self.dragging_wp_index = wp_tuple[0]
        else:
            self.movement_offset = QMouseEvent.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def initialize_wp(self, mouse_click):
        lon = GoogleMapPlotter.pix_to_rel_lon(self.GMP.center.lon, mouse_click.x() - self.GMP.width/2, self.GMP.zoom)
        lat = GoogleMapPlotter.pix_to_rel_lat(self.GMP.center.lat, mouse_click.y() - self.GMP.height/2, self.GMP.zoom)
        w = self.GB.gps_to_ned(lat, lon, 0)
        waypoint = Waypoint()
        waypoint.w = w
        return waypoint

    def clicked_on_waypoint(self, mouse_click):
        for index, waypoint in enumerate(self.waypoints):
            lat, lon, alt = self.GB.ned_to_gps(waypoint.w[0], waypoint.w[1], waypoint.w[2])
            x = self.lon_to_pix(lon)
            y = self.lat_to_pix(lat)
            mouse_x = mouse_click.x()
            mouse_y = mouse_click.y()
            if mouse_x >= x-self.waypoint_radius and mouse_x <= x+self.waypoint_radius and mouse_y >= y-self.waypoint_radius and mouse_y <= y+self.waypoint_radius:
                return (index, waypoint)
        return None

    def mouseReleaseEvent(self, QMouseEvent):
        self.dragging_wp = False
        if not self._mouse_attentive:
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def grid_viewer_toggle(self, state_integer):
        if state_integer == 2:
            self.draw_gridlines = True
        else:
            self.draw_gridlines = False

    def show_waypoint_popup(self, waypoint):
        self.wp_popup = CreateWaypointPopup(self, waypoint)
        self.wp_popup.init_create_waypoint()
        self.wp_popup.show()

    def create_wp(self, waypoint):
        self.waypoints.append(waypoint)
        self.wp_popup.close()
        #self.update()
        print('Added waypoint')

    def update_wp(self, waypoint, new_index, prev_index):
        old_waypoint = self.waypoints[new_index]
        self.waypoints[new_index] = waypoint
        self.waypoints[prev_index] = old_waypoint
        self.wp_popup.close()
        print('updated waypoint')

    def start_waypoints(self):
        for index, waypoint in enumerate(self.waypoints):
            if index == 0:
                waypoint.set_current = True
            else:
                waypoint.set_current = False
            waypoint.clear_wp_list = False
            WaypointPub.publishWaypoint(waypoint)
        print('Started Waypoints')

    def stop_waypoints(self):
        WaypointPub.clear_waypoints()

    def clear_waypoints(self):
        self.waypoints = []
        self.stop_waypoints()

    def delete_wp(self, index):
        del self.waypoints[index]
        self.wp_popup.close()

    # =====================================================
    # ==================== FOR DRAWING ====================
    # =====================================================

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        upper_left = QPoint(0, 0)
        painter.drawImage(upper_left, self.GMP.GetImage())

        if self.draw_gridlines:
            self.draw_grid(painter)
        # Draw center crosshairs (probably temporary until smartzoom feature is implemented)
        painter.setPen(QPen(QBrush(Qt.blue), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(self.GMP.width/2, self.GMP.height/2-8, self.GMP.width/2, self.GMP.height/2+8)
        painter.drawLine(self.GMP.width/2-8, self.GMP.height/2, self.GMP.width/2+8, self.GMP.height/2)
        if WaypointSub.enabled:
            self.draw_waypoints(painter)
        if ObstacleSub.enabled:
            self.draw_obstacles(painter)
        '''if PathSub.enabled:
                                    self.draw_currentpath(painter)'''
        if StateSub.enabled:
            self.draw_plane(painter)
        self.draw_waypoints(painter)
        painter.end()

    # draws gridlines at 10-meter increments
    def draw_grid(self, painter): # ++++++++++++++++++++++++++++++++++++
        painter.fillRect(QRect(0, self.GMP.height - 20, self.GMP.width, self.GMP.height), Qt.white)
        painter.fillRect(QRect(0, 0, 50, self.GMP.height - 20), Qt.white)
        painter.setPen(QPen(QBrush(Qt.black), 1.5, Qt.SolidLine, Qt.RoundCap))
        pixels_per_dist = self.grid_dist * 2**self.GMP.zoom / (156543.03392 * cos(radians(InitSub.init_latlonalt[0])))

        x_min, x_offset = divmod(GoogleMapPlotter.rel_lon_to_rel_pix(InitSub.init_latlonalt[1], self.GMP.west, self.GMP.zoom), pixels_per_dist)
        x_offset = pixels_per_dist - x_offset
        x_min = int(x_min)
        x_max = x_min + int(self.GMP.width / pixels_per_dist) + 1
        x_min += 1

        y_min, y_offset = divmod(GoogleMapPlotter.rel_lat_to_rel_pix(self.GMP.south, InitSub.init_latlonalt[0], self.GMP.zoom), pixels_per_dist)
        y_offset = pixels_per_dist - y_offset
        y_min = int(y_min)
        y_max = y_min + int(self.GMP.height / pixels_per_dist) + 1
        y_min += 1
        #print y_min, y_max

        for i, x_line in enumerate(range(x_min, x_max + 1)):
            x_coord = x_offset + i * pixels_per_dist
            painter.drawLine(x_coord, 0, x_coord, self.GMP.height)
            if self.GMP.zoom > 17:
                text_point = QPoint(x_coord + 2, self.GMP.height - 5)
                painter.drawText(text_point, QString('%d m' % (x_line * self.grid_dist)))

        for i, y_line in enumerate(range(y_min, y_max + 1)):
            y_coord = self.GMP.height - (y_offset + i * pixels_per_dist)
            painter.drawLine(0, y_coord, self.GMP.width, y_coord)
            if self.GMP.zoom > 17:
                text_point = QPoint(5, y_coord - 7)
                painter.drawText(text_point, QString('%d m' % (y_line * self.grid_dist)))

    def draw_waypoints(self, painter):
        # it can be assumed that all waypoints are converted to latlon if the sub is enabled
        font = QFont()
        font.setPixelSize(20)
        painter.setFont(font)
        for index, waypoint in enumerate(self.waypoints):
            color = QBrush(Qt.darkRed)
            painter.setPen(QPen(color, 2.5, Qt.SolidLine, Qt.RoundCap))
            lat, lon, alt = self.GB.ned_to_gps(waypoint.w[0], waypoint.w[1], waypoint.w[2])
            x = self.lon_to_pix(lon)
            y = self.lat_to_pix(lat)
            '''print(x, ',', y)
                                    sys.exit('')'''
            if x >=0 and x <= self.GMP.width and y >= 0 and y <= self.GMP.height:
                center = QPoint(x, y)
                painter.drawEllipse(center, self.waypoint_radius, self.waypoint_radius)
                diameter = self.waypoint_radius * 2
                rect = QRect(x-self.waypoint_radius, y-self.waypoint_radius, diameter, diameter)
                painter.drawText(rect, Qt.AlignCenter, str(index+1))
                '''if waypoint.chi_valid:
                                                        painter.drawLine(x, y, x+2*rad*sin(waypoint.chi_d), y-2*rad*cos(waypoint.chi_d))'''

    def draw_obstacles(self, painter):
        pass # ++++++++++++++++++++++++++++++++++++++++++

    def draw_currentpath(self, painter):
        painter.setPen(QPen(QBrush(Qt.red), 3.5, Qt.SolidLine, Qt.RoundCap))
        if PathSub.path_type == 1: # line path
            r = PathSub.r # [lat, lon]
            q = PathSub.q # unit length, NED
            scale = 200   # pixels
            pt_1 = [self.lon_to_pix(r[1]), self.lat_to_pix(r[0])]
            if pt_1[0] >=0 and pt_1[0] <= self.GMP.width and pt_1[1] >= 0 and pt_1[1] <= self.GMP.height:
                pt_2 = [pt_1[0]+scale*q[1],pt_1[1]-scale*q[0]]
                painter.drawLine(pt_1[0], pt_1[1], pt_2[0], pt_2[1])
        else:
            c = PathSub.c # [lat, lon]
            R = PathSub.rho # meters
            pt_c = [self.lon_to_pix(c[1]), self.lat_to_pix(c[0])]
            if pt_c[0] >=0 and pt_c[0] <= self.GMP.width and pt_c[1] >= 0 and pt_c[1] <= self.GMP.height:
                R_pix = R * 2**self.GMP.zoom / (156543.03392 * cos(radians(c[0])))
                painter.drawEllipse(pt_c[0]-R_pix, pt_c[1]-R_pix, 2*R_pix, 2*R_pix)

    def draw_plane(self, painter):
        if RCSub.autopilotEnabled:
            painter.setPen(QPen(QBrush(Qt.red), 5, Qt.SolidLine, Qt.RoundCap))
        else:
            painter.setPen(QPen(QBrush(Qt.cyan), 5, Qt.SolidLine, Qt.RoundCap))

        x = self.lon_to_pix(StateSub.lon)
        y = self.lat_to_pix(StateSub.lat)

        if x >=0 and x <= self.GMP.width and y >= 0 and y <= self.GMP.height:
            #print 'plane at', x, y
            chi = StateSub.chi

            pt_1_x = x + self.rotate_x(0, self.plane_h/2, chi)
            pt_1_y = y - self.rotate_y(0, self.plane_h/2, chi)
            pt_2_x = x + self.rotate_x(0, -self.plane_h/2, chi)
            pt_2_y = y - self.rotate_y(0, -self.plane_h/2, chi)
            pt_3_x = x
            pt_3_y = y
            pt_4_x = x + self.rotate_x(-self.plane_w/2, -self.plane_h/4, chi)
            pt_4_y = y - self.rotate_y(-self.plane_w/2, -self.plane_h/4, chi)
            pt_5_x = x + self.rotate_x(self.plane_w/2, -self.plane_h/4, chi)
            pt_5_y = y - self.rotate_y(self.plane_w/2, -self.plane_h/4, chi)
            pt_6_x = x + self.rotate_x(-self.plane_w/4, -2*self.plane_h/5, chi)
            pt_6_y = y - self.rotate_y(-self.plane_w/4, -2*self.plane_h/5, chi)
            pt_7_x = x + self.rotate_x(self.plane_w/4, -2*self.plane_h/5, chi)
            pt_7_y = y - self.rotate_y(self.plane_w/4, -2*self.plane_h/5, chi)

            painter.drawLine(pt_1_x, pt_1_y, pt_2_x, pt_2_y)
            painter.drawLine(pt_3_x, pt_3_y, pt_4_x, pt_4_y)
            painter.drawLine(pt_3_x, pt_3_y, pt_5_x, pt_5_y)
            painter.drawLine(pt_6_x, pt_6_y, pt_7_x, pt_7_y)
            painter.setPen(QPen(QBrush(Qt.black), 2.5, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(pt_1_x, pt_1_y, pt_2_x, pt_2_y)
            painter.drawLine(pt_3_x, pt_3_y, pt_4_x, pt_4_y)
            painter.drawLine(pt_3_x, pt_3_y, pt_5_x, pt_5_y)
            painter.drawLine(pt_6_x, pt_6_y, pt_7_x, pt_7_y)


    def lon_to_pix(self, lon): # assuming origin at upper left
        return GoogleMapPlotter.rel_lon_to_rel_pix(self.GMP.west, lon, self.GMP.zoom)

    def lat_to_pix(self, lat): # assuming origin at upper left
        return GoogleMapPlotter.rel_lat_to_rel_pix(self.GMP.north, lat, self.GMP.zoom)

    def rotate_x(self, x, y, a):
        return x * cos(a) + y * sin(a)

    def rotate_y(self, x, y, a):
        return -1 * x * sin(a) + y * cos(a)
