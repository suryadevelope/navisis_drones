"""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"""


import cv2
import numpy as np
from pyzbar.pyzbar import decode
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import argparse
import math
import RPi.GPIO as GPIO 
from threading import Thread
import time 


latt = "17.462211"
long = "78.595023"
alt = "1.5"

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

TRIG = 4  # Trigger pin of the Ultrasonic Sensor 
ECHO = 17 #Echo pin of the Ultrasonic Sensor 
GPIO.setup(TRIG,GPIO.OUT) 
GPIO.setup(ECHO,GPIO.IN) 

connection_string = "/dev/ttyAMA0"#args.connect
# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
vehicle.wait_ready(True, raise_exception=False)

#Connects to the vehicle using serial po
def sensor_data(d,o):
    
    
    msg = vehicle.message_factory.distance_sensor_encode(
        0,          # time since system boot
        5,          # min distance cm
        300,      # max distance cm
        int(d),       # current distance, must be int
        0,          # type = laser?
        0,          # onboard id, not used
        int(o), #direction
        0           # covariance, not used
    )
    print(msg)
    vehicle.send_mavlink(msg)   #Simple function to measure the distance
    point1 = LocationGlobalRelative(float(latt),float(long), float(alt))
    vehicle.simple_goto(point1)


def measure(): 
    dist1=250 
    GPIO.output(TRIG, True) 
    time.sleep(0.00001) 
    GPIO.output(TRIG, False) 
    echo_state=0 
    
    while echo_state == 0: 
        echo_state = GPIO.input(ECHO) 
        pulse_start = time.time() 
    while GPIO.input(ECHO)==1: 
        pulse_end = time.time() 
    pulse_duration = pulse_end - pulse_start 
    distance = pulse_duration * 17150 
    distance = round(distance, 2) 
    print(distance)
    if(distance<250 and distance>5): #To filter out junk values 
        dist1=distance 
        sensor_data(dist1,4) #Sends measured distance(dist1) and orientation(0) as a mavlink message. 
    else:
        dist1 = 0
        sensor_data(dist1,4) #Sends measured distance(dist1) and orientation(0) as a mavlink message. 

    return dist1 # Main code 


def objstart():
    while True:
        measure()
        time.sleep(0.2)
Thread(target = objstart).start()



vehicle.airspeed = 5
vehicle.groundspeed = 50
vehicle.parameters['LAND_SPEED'] = 25 ##Descent speed of 30cm/s
vehicle.parameters["WPNAV_SPEED"]=150
vehicle.parameters["PRX_TYPE"]=2
vehicle.parameters["OA_TYPE"]=1
vehicle.parameters["OA_BR_TYPE"]=1
vehicle.parameters["OA_LOOKAHEAD"]=2
time.sleep(50)
vehicle.parameters["OA_BR_TYPE"]=2
vehicle.parameters["OA_DB_EXPIRE"]=10
vehicle.parameters["OA_DB_QUEUE_SIZE"]=80
vehicle.parameters["OA_DB_OUTPUT"]=1



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
arm_and_takeoff(alt)
vehicle.airspeed = 5
print("Take off complete")

# Hover for 10 seconds
time.sleep(3)
print("Vehicle going to the location")
point1 = LocationGlobalRelative(float(latt),float(long), float(alt))
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)

vehicle.simple_goto(point1)
while True:
    
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        time.sleep(2)
        break
           
    time.sleep(3)
        

  
vehicle.mode = VehicleMode("LAND")
while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    # Break and return from function just below target altitude.
    if vehicle.location.global_relative_frame.alt <=0:
        print("Reached ground")
        vehicle.close() 
        break
    time.sleep(1)