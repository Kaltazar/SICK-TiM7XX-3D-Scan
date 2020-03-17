"""
Jesse Moore CPTC 2020

Module designed to collect scan data from a SICK TiM7XX LiDAR that is mounted
on a 6 axis robot arm. The robot is then moved a step and the scan is made
again. The data is stored as a text file and passed to another module for
processing
"""
import Scan_Lib.LiDAR_TiM7XX as ls
import Scan_Lib.Polar_to_Cart as pc
import robolink as rl
import robodk as rd
import datetime
import time
import os
import pandas as pd

debug = False

# Set up the API and robot
RDK = rl.Robolink()
robot = RDK.ItemUserPick('Select a robot', rl.ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected or available')

# Set options for simulation or live robot use, and scan options
RUN_ON_ROBOT = True
numberOfScans = 127
scanStep = 2  # Sets distance and direction of move on X axis
scanDelay = 1/15
scansPerStep = 50
lidarIP = '192.168.50.50'
# If running live, connect to the robot
if RUN_ON_ROBOT:
    print("Running on robot")
    robot.Connect()
    status, status_msg = robot.ConnectedState()
    if status != rl.ROBOTCOM_READY:
        print(status_msg)
        raise Exception('Failed to connect: ' + status_msg)

    RDK.setRunMode(rl.RUNMODE_RUN_ROBOT)

# Else set up simulation
else:
    print('Running simulation')
    RDK.setRunMode(rl.RUNMODE_SIMULATE)

# Set robot to scan position and set up other settings
scanStartPos = RDK.Item('Scanstart')
robotHomePos = RDK.Item('Home')
robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(RDK.Item('Scanner TCP'))
robot.setSpeed(50)
robot.setAcceleration(50)
robot.MoveL(scanStartPos)
robot.setSpeed(50)
scanPose = rd.Mat(robot.Pose())

# Connect to lidar
scan = ls.Lidar(lidarIP)
scan.connect()
if debug:
    print('LiDAR Connected')
# Create a unique filename
sd = os.path.dirname(__file__)
path = sd + '/Scans/'
filename = ('scan_' + str(datetime.datetime.now().date()) + '_' +
            str(datetime.datetime.now().time()).replace(':', '_'))
filename = filename + '.txt'
filewrite = path + filename
# Open file for writing
with open(filewrite, 'w') as fn:
    # Get the list of angles and write them to the file
    if debug:
        print('Scanning...')
    angles = scan.getAngleList()
    angleString = ' '.join(map(str, angles))
    fn.write(angleString)
    fn.write('\n')
    # Loop for number of scans required
    for i in range(numberOfScans + 1):
        # Get LiDAR measurements at current location
        distDF = pd.DataFrame()
        for n in range(scansPerStep):
            distS = pd.Series(scan.singleScan())
            distDF = pd.concat([distDF, distS], axis=1, ignore_index=True)
            time.sleep(scanDelay)
        medianSeries = distDF.median(axis=1)
        dist = medianSeries.tolist()
        distString = ' '.join(map(str, dist))
        # Calculate new position and move robot
        scanMove = scanPose.Pos()
        scanMove[0] = scanMove[0] + scanStep
        scanPose.setPos(scanMove)
        robot.MoveL(scanPose)
        # Write measurements to file
        fn.write(distString)
        fn.write('\n')
        time.sleep(scanDelay)
# Disconnect from the sensor when done
print('Scan Compleate')
scan.disconnect()
# Send robot to home position
robot.setPoseTool(RDK.Item('UR5 Dremmel TCP'))
robot.setSpeed(100)
robot.MoveJ(robotHomePos)
# Close RoboDK connection
robot.Disconnect()
# Send collected data to processing module
if debug:
    print('Sending scan for processing')
pc.polarFileToCart(path, filename, scanStep, debug)
