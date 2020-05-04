# Setup Steps

Below shows steps in installing the dependencies for ros_groundstation as well as running the test simulation

(Note: Should build catkin workspace after every new ros repository is downloaded into workspace in the src folder)

1. create catkin workspace

2. Get ROSFlight repositiory and follow all steps for installation (https://docs.rosflight.org/user-guide/ros-setup/)

2. Get the ROSFlight plugins repository (https://github.com/byu-magicc/rosflight_plugins)

3. Get the Inertial_sense_ros repository and follow all steps for installation (https://github.com/inertialsense/inertial_sense_ros)

5. Get the ROSPlane repository and follow all steps for installation (https://github.com/byu-magicc/rosplane)

6. Get the ros_groundstation repository and follow all steps for installation (https://github.com/jacksondelametter/ros_groundstation)

7. Set up a map static api key and add the key to the key.xml file inside the ros_groundation repository. (https://developers.google.com/maps/documentation/maps-static/intro#api)

8. Launch ROSCore, and ROSFlight. 

9. Launch ROSPlane using roslaunch rosplane_sim fixedwing.launch (Gazebo should show up)

10. Go to ros_groundstation directory, switch to final_waypoint_features branch using git checkout -b final_waypoint_features --track origin/final_waypoint_features

9. Luanch ros_groundstation using roslaunch ros_groundstation gs_fixedwing.launch

10. In Gazebo simulator, run the simulation by clicking the play button on the bottom of the Gazebo window

11. In ros_groundstation, you should see the plane moving on the map, It will be following invisible waypoints

12. Click the clearn button and plane should hover around origin. 

13. How to use ros_groundstation

- To create waypoint, right click on map and add options in popup window. 
- To edit waypoint, right click on waypoint on map
- To move waypoint, left click on waypoint and move
- To clear all waypoints, hit clear button above map. This will also clear waypoint paths
- To start waypoint paths, hit start above map. Anytime waypoint is edited, you must hit start for changes to take effect.
- To stop waypoint paths, hit stop above map. 
