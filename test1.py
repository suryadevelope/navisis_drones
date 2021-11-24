"""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"""


import cv2
import numpy as np
from pyzbar.pyzbar import decode
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import argparse
import math


parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
print(args.connect)
connection_string = "/dev/ttyAMA0"#args.connect
# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
vehicle.wait_ready(True, raise_exception=False)
latt = "17.462211"
long = "78.595023"
vehicle.airspeed = 5
vehicle.groundspeed = 50
vehicle.parameters['LAND_SPEED'] = 25 ##Descent speed of 30cm/s
vehicle.parameters["WPNAV_SPEED"]=150



def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5



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
        
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)
        
print(vehicle.battery.voltage)
#arm_and_takeoff(1)
vehicle.airspeed = 5
print("Take off complete")

# Hover for 10 seconds
time.sleep(3)
print("Vehicle going to the location")
point1 = LocationGlobalRelative(float(latt),float(long), 1)
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)
#vehicle.simple_goto(point1)
while True:
    
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        time.sleep(2)
        break
           
    time.sleep(3)
        
def decoder(image):
    gray_img = cv2.cvtColor(image,0)
    barcode = decode(gray_img)

    for obj in barcode:
        points = obj.polygon
        (x,y,w,h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)

        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type
        string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)
        
        cv2.putText(frame, string, (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0), 2)
        print("Barcode: "+barcodeData +" | Type: "+barcodeType)
        while True :
             if barcodeData == "surya":
                 print(" Altitude: ", vehicle.location.global_relative_frame.alt)
                 print("Vehicle is landing")
                 break
        
        
        vehicle.mode = VehicleMode("LAND")
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt <=0:
                print("Reached ground")
                vehicle.close() 
                break
            time.sleep(1)

               
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    decoder(frame)
    cv2.imshow('Image', frame)
    code = cv2.waitKey(1)
  
