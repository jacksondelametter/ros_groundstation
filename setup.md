# Setup Steps

(Note: Should build catkin workspace after every new ros repository is downloaded into workspace in the src folder)

1. create catkin workspace

2. Get ROSFlight repositiory and follow all steps for installation (https://docs.rosflight.org/user-guide/ros-setup/)

2. Get the ROSFlight plugins repository

3. Get the Inertial_sense_ros repository and follow all steps for installation (https://github.com/inertialsense/inertial_sense_ros)

5. Get the ROSPlane repository and follow all steps for installation (https://github.com/byu-magicc/rosplane)

6. Get the ros_groundstation repository and follow all steps for installation (https://github.com/jacksondelametter/ros_groundstation)

7. Set up a map static api key and add the key to the key.xml file inside the ros_groundation repository. (https://developers.google.com/maps/documentation/maps-static/intro#api)

8. Run using roslaunch ros_groundstation gs_fixedwing.launch