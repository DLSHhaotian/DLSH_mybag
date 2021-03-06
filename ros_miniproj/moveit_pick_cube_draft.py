#!/usr/bin/env python
#import roslib
#roslib.load_manifest('hello_ros')

import sys
import copy
import rospy
import tf_conversions
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import tf
import shape_msgs.msg as shape_msgs
from sensor_msgs.msg import JointState
from numpy import zeros, array, linspace
from math import ceil

def move_pick_cube():
    print ("============ Starting setup ============")
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('move_pick_cube',
                    anonymous=True)

    robot = moveit_commander.RobotCommander()
    scene = moveit_commander.PlanningSceneInterface()
    group = moveit_commander.MoveGroupCommander("Arm")
    end_effector_link=group.get_end_effector_link()
    #group.set_pose_reference_frame(group.get_end_effector_link())
    # trajectories for RVIZ to visualize.
    display_trajectory_publisher = rospy.Publisher(
        '/move_group/display_planned_path',
        moveit_msgs.msg.DisplayTrajectory)

    print ("============ Reference frame: %s" % group.get_planning_frame())
    print ("============ End effector frame: %s" % group.get_end_effector_link())
    print ("============ Robot Groups:")
    print (robot.get_group_names())
    print ("============ Printing robot state")
    print (robot.get_current_state())
    print ("============")
    print ("============put cubes and bucket into moveit workspace")
    # If we're coming from another script we might want to remove the objects
    for i in xrange(0, 6):
        if "cube{}".format(i) in scene.get_known_object_names():
            scene.remove_world_object("cube{}".format(i))
    if "bucket" in scene.get_known_object_names():
        scene.remove_world_object("bucket")
    ##put cubes and bucket into moveit workspace
    ##load param into a list
    cube_bucket_orient=rospy.get_param("cube_bucket_orientRPY")
    bucket_pose=rospy.get_param("bucket_XYZ")
    cube_num=rospy.get_param("cube_num")
    table_height=0.75#table height=0.8
    orient_quat = geometry_msgs.msg.Quaternion(*tf_conversions.transformations.quaternion_from_euler(cube_bucket_orient[0],cube_bucket_orient[1],cube_bucket_orient[2]))
    cube_pose_list=list()
    for i in xrange(0, cube_num):
      if rospy.has_param("cube{}_XYZ".format(i)):
            cube_pose_list.append(rospy.get_param("cube{}_XYZ".format(i)))
            cube_pose_list[i][2]=table_height

    ##prepare the cubes info

    cube_info = geometry_msgs.msg.PoseStamped()
    cube_info.header.frame_id="robot_base"
    for i in xrange(0, cube_num):
        cube_info.pose.position.x = cube_pose_list[i][0]
        cube_info.pose.position.y = cube_pose_list[i][1]
        cube_info.pose.position.z = table_height#table height
        cube_info.pose.orientation = orient_quat
        scene.add_box("cube{}".format(i), cube_info, (0.05,0.05,0.05))##found in cubic.urdf
    #prepare the bucket info
    bucket_info=geometry_msgs.msg.PoseStamped()
    bucket_info.header.frame_id = "robot_base"
    bucket_info.pose.position.x = bucket_pose[0]
    bucket_info.pose.position.y = bucket_pose[1]
    bucket_info.pose.position.z = table_height
    bucket_info.pose.orientation = orient_quat
    scene.add_box("bucket",bucket_info,(0.3,0.3,0.3))##cannot found in bucket.dae
    print ("============moveit workspace loading finished")


    ## setup the planner parameters
    group.set_goal_orientation_tolerance(0.01)
    group.set_goal_tolerance(0.01)
    group.set_goal_joint_tolerance(0.01)
    group.set_num_planning_attempts(100)

    ##prepare the waypoints
    hand_pick_quat=geometry_msgs.msg.Quaternion(0.347709304721,-0.646715871525,0.298597553716,0.609669026475)
    waypoints1=list()
    pose_goal=group.get_current_pose(end_effector_link).pose
    ini_pose=pose_goal
    print(pose_goal)
    waypoints1.append(pose_goal)

    pose_goal.orientation = hand_pick_quat
    print(pose_goal)
    waypoints1.append(pose_goal)

    (plan1, fraction) = group.compute_cartesian_path(waypoints1, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan1)
    display_trajectory_publisher.publish(display_trajectory);
    print ("============ Waiting while plan1 is visualized (again)...")
    rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan1, wait=True)
    rospy.sleep(1.)
    ########################### go to the upper of cube
    waypoints12 = list()
    pose_goal12 = group.get_current_pose(end_effector_link).pose
    ini_pose12 = pose_goal12
    print(pose_goal12)
    waypoints12.append(pose_goal12)

    pose_goal12.position.x = cube_pose_list[0][0]
    pose_goal12.position.y = cube_pose_list[0][1]
    pose_goal12.position.z = cube_pose_list[0][2] + 0.6
    pose_goal12.orientation = hand_pick_quat
    print(pose_goal12)
    waypoints12.append(pose_goal12)

    (plan12, fraction) = group.compute_cartesian_path(waypoints12, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan12)
    display_trajectory_publisher.publish(display_trajectory);
    print ("============ Waiting while plan1 is visualized (again)...")
    rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan12, wait=True)
    rospy.sleep(2.)
    ########################go down to the cube
    waypoints2 = list()
    pose_goal2 = group.get_current_pose(end_effector_link).pose
    ini_pose2 = pose_goal2
    print(pose_goal2)
    waypoints2.append(pose_goal2)

    pose_goal2.position.x = cube_pose_list[0][0]
    pose_goal2.position.y = cube_pose_list[0][1]
    pose_goal2.position.z = cube_pose_list[0][2] + 0.5
    pose_goal2.orientation = hand_pick_quat
    print(pose_goal2)
    waypoints2.append(pose_goal2)
    pose_goal2.position.x = cube_pose_list[0][0]
    pose_goal2.position.y = cube_pose_list[0][1]
    pose_goal2.position.z = cube_pose_list[0][2] + 0.4
    pose_goal2.orientation = hand_pick_quat
    print(pose_goal2)
    waypoints2.append(pose_goal2)
    pose_goal2.position.x = cube_pose_list[0][0]
    pose_goal2.position.y = cube_pose_list[0][1]
    pose_goal2.position.z = cube_pose_list[0][2] + 0.15
    pose_goal2.orientation = hand_pick_quat
    print(pose_goal2)
    waypoints2.append(pose_goal2)
    (plan2, fraction) = group.compute_cartesian_path(waypoints2, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan2)
    display_trajectory_publisher.publish(display_trajectory)
    #print ("============ Waiting while plan1 is visualized (again)...")
    #rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan2, wait=True)
    rospy.sleep(1.)


    ##############################################################
    ################################################close the hand
    pub = rospy.Publisher("/jaco/joint_control", JointState, queue_size=1)

    currentJointState = rospy.wait_for_message("/joint_states", JointState)
    print ('Received!')
    currentJointState.header.stamp = rospy.get_rostime()
    tmp = 0.7
    # tmp_tuple=tuple([tmp] + list(currentJointState.position[1:]))
    currentJointState.position = tuple(list(currentJointState.position[:6]) + [tmp] + [tmp] + [tmp])
    rate = rospy.Rate(10)  # 10hz
    for i in range(3):
        pub.publish(currentJointState)
        print ('Published!')
        rate.sleep()

    print ('end!')
    rospy.sleep(5.)
    #############################################
    #############################################hand up

    waypoints3 = list()
    pose_goal3 = group.get_current_pose(end_effector_link).pose
    ini_pose3 = pose_goal3
    print(pose_goal3)

    waypoints3.append(pose_goal3)
    pose_goal3.position.z = cube_pose_list[0][2] + 0.3#have to use the x,y of current pose instead of cube's pose when going up
    pose_goal3.orientation = hand_pick_quat
    print(pose_goal3)
    waypoints3.append(pose_goal3)
    pose_goal3.position.z = cube_pose_list[0][2] + 0.4
    pose_goal3.orientation = hand_pick_quat
    print(pose_goal3)
    waypoints3.append(pose_goal3)
    pose_goal3.position.z = cube_pose_list[0][2] + 0.5
    pose_goal3.orientation = hand_pick_quat
    print(pose_goal3)
    waypoints3.append(pose_goal3)
    pose_goal3.position.z = cube_pose_list[0][2] + 0.7
    pose_goal3.orientation = hand_pick_quat
    print(pose_goal3)
    waypoints3.append(pose_goal3)
    (plan3, fraction) = group.compute_cartesian_path(waypoints3, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan3)
    display_trajectory_publisher.publish(display_trajectory)
    # print ("============ Waiting while plan1 is visualized (again)...")
    # rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan3, wait=True)
    rospy.sleep(1.)


    ####################################################################
    ###########################################go to the upper of bucket
    print("go to the upper of bucket")
    waypoints34 = list()
    pose_goal34 = group.get_current_pose(end_effector_link).pose
    ini_pose34 = pose_goal34
    print(pose_goal34)
    waypoints34.append(pose_goal34)
    pose_goal34.position.x = bucket_pose[0]
    pose_goal34.position.y = bucket_pose[1]
    pose_goal34.position.z = table_height + 0.7
    pose_goal34.orientation = hand_pick_quat
    print(pose_goal34)
    waypoints34.append(pose_goal34)
    (plan34, fraction) = group.compute_cartesian_path(waypoints34, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan34)
    display_trajectory_publisher.publish(display_trajectory)
    # print ("============ Waiting while plan1 is visualized (again)...")
    # rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan34, wait=True)
    rospy.sleep(1.)
    ############################################go to bucket
    waypoints4 = list()
    pose_goal4 = group.get_current_pose(end_effector_link).pose
    ini_pose4 = pose_goal4
    print(pose_goal4)
    waypoints4.append(pose_goal4)
    pose_goal4.position.x = bucket_pose[0]
    pose_goal4.position.y = bucket_pose[1]
    pose_goal4.position.z = table_height + 0.6
    pose_goal4.orientation = hand_pick_quat
    print(pose_goal4)
    waypoints4.append(pose_goal4)

    pose_goal4.position.x = bucket_pose[0]
    pose_goal4.position.y = bucket_pose[1]
    pose_goal4.position.z = table_height + 0.5
    pose_goal4.orientation = hand_pick_quat
    print(pose_goal4)
    waypoints4.append(pose_goal4)

    (plan4, fraction) = group.compute_cartesian_path(waypoints4, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan4)
    display_trajectory_publisher.publish(display_trajectory)
    # print ("============ Waiting while plan1 is visualized (again)...")
    # rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan4, wait=True)
    rospy.sleep(1.)
    #################################open the hand
    currentJointState = rospy.wait_for_message("/joint_states", JointState)
    print ('Received!')
    currentJointState.header.stamp = rospy.get_rostime()
    tmp = 0.005
    # tmp_tuple=tuple([tmp] + list(currentJointState.position[1:]))
    currentJointState.position = tuple(list(currentJointState.position[:6]) + [tmp] + [tmp] + [tmp])
    rate = rospy.Rate(10)  # 10hz
    for i in range(3):
        pub.publish(currentJointState)
        print ('Published!')
        rate.sleep()

    print ('end!')

    #############################################
    #############################################hand up

    waypoints5 = list()
    pose_goal5 = group.get_current_pose(end_effector_link).pose
    ini_pose5 = pose_goal5
    print(pose_goal5)
    waypoints5.append(pose_goal5)
    pose_goal5.position.z = table_height + 0.6  # have to use the x,y of current pose instead of bucket's pose when going up
    pose_goal5.orientation = hand_pick_quat
    print(pose_goal5)
    waypoints5.append(pose_goal5)
    pose_goal5.position.z = table_height + 0.7
    pose_goal5.orientation = hand_pick_quat
    print(pose_goal5)
    waypoints5.append(pose_goal5)

    (plan5, fraction) = group.compute_cartesian_path(waypoints5, 0.01, 0.0)

    print ("============ Waiting while RVIZ displays plan1...")
    rospy.sleep(0.5)

    print ("============ Visualizing plan1")
    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan5)
    display_trajectory_publisher.publish(display_trajectory)
    # print ("============ Waiting while plan1 is visualized (again)...")
    # rospy.sleep(2.)

    ## Moving to a pose goal
    group.execute(plan5, wait=True)
    rospy.sleep(1.)
    # END_TUTORIAL
    print ("============ STOPPING")
    R = rospy.Rate(10)
    while not rospy.is_shutdown():
        R.sleep()


if __name__=='__main__':
  try:
    move_pick_cube()
  except rospy.ROSInterruptException:
    pass
