import rospy
from rosplane_msgs.msg import Waypoint

class WaypointPub:

	waypoint_topic = None
	waypoint_pub = None

	@staticmethod
	def updateWaypointPub(waypoint_topic):
		print 'Setting up plublishing to ', waypoint_topic
		WaypointPub.reset()
		WaypointPub.waypoint_topic = waypoint_topic
		if WaypointPub.waypoint_topic is not None:
			WaypointPub.waypoint_pub = rospy.Publisher(waypoint_topic, Waypoint)

	@staticmethod
	def publishWaypoint(waypoint):
		print 'published waypoint'
		WaypointPub.waypoint_pub.publish(waypoint)

	@staticmethod
	def reset():
		if WaypointPub.waypoint_topic is not None:
			WaypointPub.waypoint_pub.unregister()

	@staticmethod
	def closePublisher():
		print("closing publisher")
		WaypointPub.reset()

	@staticmethod
	def clear_waypoints():
		print('Clearing waypoints')
		waypoint = Waypoint()
		waypoint.clear_wp_list = True
		WaypointPub.publishWaypoint(waypoint)


