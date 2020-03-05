from python_qt_binding import loadUi
from PyQt5.Qt import *
from PyQt5.QtGui import *
QString = type("")

import os, rospy

from .map_subscribers import *
from .map_publishers import *

PWD = os.path.dirname(os.path.abspath(__file__))

class OpWindow(QWidget):
    def __init__(self, marble, uifname = 'op_window.ui'):
        super(OpWindow, self).__init__()
        self.marble = marble
        ui_file = os.path.join(PWD, 'resources', uifname)
        loadUi(ui_file, self)
        self.setObjectName(uifname)

        # Parse NED_with_GPS_defaults ==================================================
        self.NEDwGPS_tab = QWidget()
        self.tab_widget.addTab(self.NEDwGPS_tab, QString('Principle Subscibers and Publishers'))
        description = 'All ROS information is exchanged with the plane in NED format, and the plane\n' + \
            'may provide an initial GPS position for accurate latlong rendering.'
        layout = QVBoxLayout()
        layout.addWidget(QLabel(QString(description)))

        label = 'GPS init Subscriber'
        checked = rospy.get_param('gpsInitSubChecked', True)
        topic = rospy.get_param('gpsInitSubTopic', '/state')
        pubsub_layout = QBoxLayout(0) # for combining the checkbox and text field
        self.NEDwGPS_gisub_checkbox = QCheckBox(QString(label))
        self.NEDwGPS_gisub_checkbox.setChecked(checked)
        self.NEDwGPS_gisub_checkbox.stateChanged[int].connect(self.handle_gisub_checkbox)
        pubsub_layout.addWidget(self.NEDwGPS_gisub_checkbox)
        self.NEDwGPS_gisub_textedit = QTextEdit(QString(topic))
        self.handle_gisub_checkbox(checked)
        pubsub_layout.addWidget(self.NEDwGPS_gisub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'State Subscriber'
        checked = rospy.get_param('stateSubChecked', True)
        topic = rospy.get_param('stateSubTopic', '/state')
        pubsub_layout = QBoxLayout(0) # for combining the checkbox and text field
        self.NEDwGPS_statesub_checkbox = QCheckBox(QString(label))
        self.NEDwGPS_statesub_checkbox.setChecked(checked)
        self.NEDwGPS_statesub_checkbox.stateChanged[int].connect(self.handle_statesub_checkbox)
        pubsub_layout.addWidget(self.NEDwGPS_statesub_checkbox)
        self.NEDwGPS_statesub_textedit = QTextEdit(QString(topic))
        self.handle_statesub_checkbox(checked)
        pubsub_layout.addWidget(self.NEDwGPS_statesub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Path Subscriber'
        checked = rospy.get_param('pathSubChecked', True)
        topic = rospy.get_param('pathSubTopic', '/current_path')
        pubsub_layout = QBoxLayout(0) # for combining the checkbox and text field
        self.NEDwGPS_pathsub_checkbox = QCheckBox(QString(label))
        self.NEDwGPS_pathsub_checkbox.setChecked(checked)
        self.NEDwGPS_pathsub_checkbox.stateChanged[int].connect(self.handle_pathsub_checkbox)
        pubsub_layout.addWidget(self.NEDwGPS_pathsub_checkbox)
        self.NEDwGPS_pathsub_textedit = QTextEdit(QString(topic))
        self.handle_pathsub_checkbox(checked)
        pubsub_layout.addWidget(self.NEDwGPS_pathsub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Waypoint Subscriber'
        checked = rospy.get_param('waypointSubChecked', True)
        topic = rospy.get_param('waypointSubTopic', '/waypoint_path')
        pubsub_layout = QBoxLayout(0) # for combining the checkbox and text field
        self.NEDwGPS_wpsub_checkbox = QCheckBox(QString(label))
        self.NEDwGPS_wpsub_checkbox.setChecked(checked)
        self.NEDwGPS_wpsub_checkbox.stateChanged[int].connect(self.handle_wpsub_checkbox)
        pubsub_layout.addWidget(self.NEDwGPS_wpsub_checkbox)
        self.NEDwGPS_wpsub_textedit = QTextEdit(QString(topic))
        self.handle_wpsub_checkbox(checked)
        pubsub_layout.addWidget(self.NEDwGPS_wpsub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Waypoint Publisher'
        checked = rospy.get_param('waypointPubChecked', False)
        topic = rospy.get_param('waypointPubTopic', '/waypoint_path')
        pubsub_layout = QBoxLayout(0) # for combining the checkbox and text field
        self.NEDwGPS_wppub_checkbox = QCheckBox(QString(label))
        self.NEDwGPS_wppub_checkbox.setChecked(checked)
        self.NEDwGPS_wppub_checkbox.stateChanged[int].connect(self.handle_wppub_checkbox)
        pubsub_layout.addWidget(self.NEDwGPS_wppub_checkbox)
        self.NEDwGPS_wppub_textedit = QTextEdit(QString(topic))
        self.handle_wppub_checkbox(checked)
        pubsub_layout.addWidget(self.NEDwGPS_wppub_textedit)
        layout.addLayout(pubsub_layout)

        self.NEDwGPS_tab.setLayout(layout)

        # Parse misc_defaults ====================================================================
        self.MD_tab = QWidget()
        self.tab_widget.addTab(self.MD_tab, QString('Miscellaneous'))
        layout = QVBoxLayout()

        label = 'RC Raw Subscriber'
        checked = rospy.get_param('rcRawSubChecked', True)
        topic = rospy.get_param('rcRawSubTopic', '/rc_raw')
        pubsub_layout = QBoxLayout(0)
        self.MD_rcsub_checkbox = QCheckBox(QString(label))
        self.MD_rcsub_checkbox.setChecked(checked)
        self.MD_rcsub_checkbox.stateChanged[int].connect(self.handle_rcsub_checkbox)
        pubsub_layout.addWidget(self.MD_rcsub_checkbox)
        self.MD_rcsub_textedit = QTextEdit(QString(topic))
        self.handle_rcsub_checkbox(checked)
        pubsub_layout.addWidget(self.MD_rcsub_textedit)
        channel_layout = QVBoxLayout()
        channel_layout.addWidget(QLabel(QString("Autopilot Toggle Channel:")))
        self.MD_rcsub_channel = QComboBox()
        self.MD_rcsub_channel.clear()
        channel_list = ['5', '6', '7', '8']
        channel = rospy.get_param('rcRawChannel', '6')
        self.MD_rcsub_channel.addItems(channel_list)
        try:
            index = channel_list.index(str(channel))
        except:
            index = 0
        self.MD_rcsub_channel.setCurrentIndex(index)
        self.MD_rcsub_channel.currentIndexChanged[str].connect(self.update_rc_channel)
        channel_layout.addWidget(self.MD_rcsub_channel)
        pubsub_layout.addLayout(channel_layout)
        layout.addLayout(pubsub_layout)

        label = 'GPS Data Subscriber'
        checked = rospy.get_param('gpsDataSubChecked', True)
        topic = rospy.get_param('gpsDataSubTopic', '/gps/data')
        pubsub_layout = QBoxLayout(0)
        self.MD_gpssub_checkbox = QCheckBox(QString(label))
        self.MD_gpssub_checkbox.setChecked(checked)
        self.MD_gpssub_checkbox.stateChanged[int].connect(self.handle_gpssub_checkbox)
        pubsub_layout.addWidget(self.MD_gpssub_checkbox)
        self.MD_gpssub_textedit = QTextEdit(QString(topic))
        self.handle_gpssub_checkbox(checked)
        pubsub_layout.addWidget(self.MD_gpssub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Controller Internals Subscriber'
        checked = rospy.get_param('controllerInternalsSubChecked', True)
        topic = rospy.get_param('controllerInternalsSubTopic', '/controller_inners')
        pubsub_layout = QBoxLayout(0)
        self.MD_cisub_checkbox = QCheckBox(QString(label))
        self.MD_cisub_checkbox.setChecked(checked)
        self.MD_cisub_checkbox.stateChanged[int].connect(self.handle_cisub_checkbox)
        pubsub_layout.addWidget(self.MD_cisub_checkbox)
        self.MD_cisub_textedit = QTextEdit(QString(topic))
        self.handle_cisub_checkbox(checked)
        pubsub_layout.addWidget(self.MD_cisub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Controller Commands Subscriber'
        checked = rospy.get_param('controllerCommandsSubChecked', True)
        topic = rospy.get_param('controllerCommandsSubTopic', '/controller_commands')
        pubsub_layout = QBoxLayout(0)
        self.MD_ccsub_checkbox = QCheckBox(QString(label))
        self.MD_ccsub_checkbox.setChecked(checked)
        self.MD_ccsub_checkbox.stateChanged[int].connect(self.handle_ccsub_checkbox)
        pubsub_layout.addWidget(self.MD_ccsub_checkbox)
        self.MD_ccsub_textedit = QTextEdit(QString(topic))
        self.handle_ccsub_checkbox(checked)
        pubsub_layout.addWidget(self.MD_ccsub_textedit)
        layout.addLayout(pubsub_layout)

        label = 'Obstacle Subscriber'
        checked = rospy.get_param('obstacleSubChecked', False)
        topic = rospy.get_param('obstacleSubTopic', '/obstacles')
        pubsub_layout = QBoxLayout(0)
        self.MD_obssub_checkbox = QCheckBox(QString(label))
        self.MD_obssub_checkbox.setChecked(checked)
        self.MD_obssub_checkbox.stateChanged[int].connect(self.handle_obssub_checkbox)
        pubsub_layout.addWidget(self.MD_obssub_checkbox)
        self.MD_obssub_textedit = QTextEdit(QString(topic))
        self.handle_obssub_checkbox(checked)
        pubsub_layout.addWidget(self.MD_obssub_textedit)
        layout.addLayout(pubsub_layout)

        self.MD_tab.setLayout(layout)

    def handle_statesub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.NEDwGPS_statesub_textedit.toPlainText())
        if checked:
            StateSub.updateStateTopic(topic_name)
        else:
            StateSub.closeSubscriber()

    def handle_gisub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.NEDwGPS_gisub_textedit.toPlainText())
        if checked:
            InitSub.updateGPSInitTopic(topic_name)
        else:
            InitSub.updateInitLatLonAlt(self.marble.latlonalt)

    def handle_pathsub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.NEDwGPS_pathsub_textedit.toPlainText())
        if checked:
            PathSub.updatePathTopic(topic_name)
        else:
            PathSub.closeSubscriber()

    def handle_wpsub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.NEDwGPS_wpsub_textedit.toPlainText())
        if checked:
            WaypointSub.updateWaypointTopic(topic_name)
        else:
            WaypointSub.closeSubscriber()

    def handle_wppub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.NEDwGPS_wppub_textedit.toPlainText())
        if checked:
            WaypointPub.updateWaypointPub(topic_name)
        else:
            WaypointPub.closePublisher()

    def handle_gpssub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.MD_gpssub_textedit.toPlainText())
        if checked:
            GPSDataSub.updateGPSDataTopic(topic_name)
        else:
            GPSDataSub.closeSubscriber()

    def handle_obssub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.MD_obssub_textedit.toPlainText())
        if checked:
            ObstacleSub.updateObstacleTopic(topic_name)
        else:
            ObstacleSub.closeSubscriber()

    def handle_rcsub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.MD_rcsub_textedit.toPlainText())
        if checked:
            RCSub.updateRCRawTopic(topic_name)
        else:
            RCSub.closeSubscriber()

    def handle_cisub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.MD_cisub_textedit.toPlainText())
        if checked:
            ConInSub.updateConInTopic(topic_name)
        else:
            ConInSub.closeSubscriber()

    def handle_ccsub_checkbox(self, state_integer):
        checked = state_integer
        topic_name = str(self.MD_ccsub_textedit.toPlainText())
        if checked:
            ConComSub.updateConComTopic(topic_name)
        else:
            ConComSub.closeSubscriber()

    def update_rc_channel(self, new_index):
        RCSub.updateRCChannel(int(new_index))
