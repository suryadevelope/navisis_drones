"""
NOTE: be sure to be using the latest dronekit. 
pip3 install dronekit
sudo pip uninstall pymavlink

cd dronekit-python
git pull

sudo python setup.py build
sudo python setup.py install

Be sure the RASPI CAMERA driver is correctly acivated -> type the following
modprobe bcm2835-v4l2 


"""
import pyzbar.pyzbar as pyzbar
import cv2
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal
import numpy as np
import argparse
import math
import time
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='')
args = parser.parse_args()


# -- Connect to the vehicle
print('Connecting...')
connection_string = "/dev/ttyAMA0"  # args.connect


cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, timeout=60, baud=921600)



horizontal_fov = 62.2 * (math.pi / 180 ) ##Pi cam V1: 53.5 V2: 62.2
vertical_fov = 48.8 * (math.pi / 180)    ##Pi cam V1: 41.41 V2: 48.8
horizontal_resolution = 640
vertical_resolution = 480




def arm_and_takeoff(aTargetAltitude):
   

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    # (otherwise the command after Vehicle.simple_takeoff will execute
    #  immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


#arm_and_takeoff(1.5)

time.sleep(3)
vehicle.parameters['PLND_ENABLED'] = 1
vehicle.parameters['PLND_TYPE'] = 1 ##1 for companion computer
vehicle.parameters['PLND_EST_TYPE'] = 0 ##0 for raw sensor, 1 for kalman filter pos estimation
vehicle.parameters['LAND_SPEED'] = 5 ##Descent speed of 30cm/s



def send_land_message(x,y):
    msg = vehicle.message_factory.landing_target_encode(
        0,
        0,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
        x,
        y,
        0,
        0,
        0,)
    vehicle.send_mavlink(msg)
    vehicle.flush()

while True:

    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    data, bbox, _ = detector.detectAndDecode(img)
    decodedObjects = pyzbar.decode(img)

    for decodedObject in decodedObjects:
        points = decodedObject.polygon
        left = decodedObject.rect[0]
        top = decodedObject.rect[1]
        height = decodedObject.rect[3]
        width = decodedObject.rect[2]
        data = decodedObject.data
        
        points = decodedObject.polygon
        if len(points) > 4:
            hull = cv2.convexHull(
                np.array([points for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points

        n = len(hull)
        # draw the lines on the QR code 
        for j in range(0, n):
            # print(j, "      ", (j + 1) % n, "    ", n)

            cv2.line(img, hull[j], hull[(j + 1) % n], (0, 255, 0), 2)
        # finding width of QR code in the image 
        x, x1 = hull[0][0], hull[1][0]
        y, y1 = hull[0][1], hull[1][1]
        
        Pos = hull[3]

        #print(data)
        # If the points do not form a quad, find convex hull
        if len(points) > 4:
            hull = cv2.convexHull(
                np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points

        # Number of points in the convex hull
        n = len(hull)

        # Draw the convext hull
        for j in range(0, n):
            cv2.line(cv2.IMREAD_LOAD_GDAL, hull[j], hull[(j+1) % n], (255, 0, 0), 3)

        ymin = (int(top+(height/2)))/100.0
        xmin = (int(left+(width/2)))/100.0
        print(ymin, xmin)

        uav_location = vehicle.location.global_relative_frame
       
            
        print(uav_location.alt)
        #if uav_location.alt >= 0.5:
        if data == b'surya':
            z_cm = uav_location.alt*100.0
            cv2.circle(img,(int(top+(width/2)),int(top+(height/2))),5,(255,0,0),-1)
            x_avg = xmin*.25
            y_avg = ymin*.25
    
            x_ang = (x_avg - horizontal_resolution*.5)*(horizontal_fov/horizontal_resolution)
            y_ang = (y_avg - vertical_resolution*.5)*(vertical_fov/vertical_resolution)
            if vehicle.mode!='LAND':
                vehicle.mode = VehicleMode('LAND')
                while vehicle.mode!='LAND':
                    time.sleep(1)
                print("------------------------")
                print("Vehicle now in LAND mode")
                print("------------------------")
                send_land_message(x_ang,y_ang)
            else:
                send_land_message(x_ang,y_ang)
                pass
            print("X CENTER PIXEL: "+str(x_avg)+" Y CENTER PIXEL: "+str(y_avg))
            print("QRCODE POSITION: x=" +str(xmin)+" y= "+str(ymin)+" z="+str(z_cm))
            break      
                    
                    
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break
# free camera object and exit
cap.release()
cv2.destroyAllWindows()
