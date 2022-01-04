from pymavlink import mavutil
import time
import RPi.GPIO as GPIO 
from threading import Thread
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink.dialects.v20 import ardupilotmega as mavlink2
import math
import datetime



latt = "17.461918"
long = "78.592785"
alt = 1.5

vehicle = connect("/dev/ttyAMA0", wait_ready=True, baud=921600)
vehicle.wait_ready(True, raise_exception=False)

vehicle.parameters['LAND_SPEED'] = 25 ##Descent speed of 30cm/s
vehicle.parameters["WPNAV_SPEED"]=80
#vehicle.parameters["PRX_TYPE"]=2
vehicle.parameters["OA_TYPE"]=1
vehicle.parameters["OA_LOOKAHEAD"]=2
vehicle.parameters["OA_BR_LOOKAHEAD"]=3
vehicle.parameters["OA_MARGIN_MAX"]=1.5
# vehicle.parameters["OA_BR_TYPE"]=1
# vehicle.parameters["OA_DB_EXPIRE"]=10
# vehicle.parameters["OA_DB_QUEUE_SIZE"]=100
# vehicle.parameters["OA_DB_OUTPUT"]=1
print("connected")
GPIO.cleanup()
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

obstacledist = 70
vehicleheading = 0

distance = 1
distancespeed = 1

RIGHTTRIG = 18  # Trigger pin of the Ultrasonic Sensor 
RIGHTECHO = 23 #Echo pin of the Ultrasonic Sensor

LEFTTRIG = 24
LEFTECHO = 25

FRONTTRIG = 4
FRONTECHO = 17

BACKTRIG = 27
BACKECHO = 22

sonardist ={}

right = 300
left = 300
front = 300
back = 300
UNIT16_MAX = 251


GPIO.setup(RIGHTTRIG,GPIO.OUT) 
GPIO.setup(RIGHTECHO,GPIO.IN) 
GPIO.setup(LEFTTRIG,GPIO.OUT) 
GPIO.setup(LEFTECHO,GPIO.IN) 
GPIO.setup(FRONTTRIG,GPIO.OUT) 
GPIO.setup(FRONTECHO,GPIO.IN) 
GPIO.setup(BACKTRIG,GPIO.OUT) 
GPIO.setup(BACKECHO,GPIO.IN) 

obstacledata={}
obstacledata["ddl"]={}


def send_distance_message():
    global front
    abc = [int(front),UNIT16_MAX, UNIT16_MAX,UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, 
    UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, 
    UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, 
    UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, 
    UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, 
    UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX,
     UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX, UNIT16_MAX]
    
    ts = datetime.datetime.now().timestamp()
    print(ts)
    msg = mavlink2.MAVLink_obstacle_distance_message(
        int(ts), #time
        1, #sensor type
        abc, # abc is usually the array of 72 elements
        15, #angular width
        10, #min distance
        250, #max distance
        15,#https://mavlink.io/en/messages/common.html#OBSTACLE_DISTANCE
        -40,
        12
        )
    time.sleep(0.1)
    if vehicle.location.global_relative_frame.alt  >= float(alt)-0.5:
        vehicle.send_mavlink(msg)
        front=251
        print(msg)
        vehicle.flush()


def rightsonar(): 
    global right
    while True:
        dist1=251
        GPIO.output(RIGHTTRIG, True) 
        time.sleep(0.00001) 
        GPIO.output(RIGHTTRIG, False) 
        echo_state=0 
        
        while echo_state == 0: 
            echo_state = GPIO.input(RIGHTECHO) 
            pulse_start = time.time() 
        while GPIO.input(RIGHTECHO)==1: 
            pulse_end = time.time() 
        pulse_duration = pulse_end - pulse_start 
        distance = pulse_duration * 17150 
        distance = round(distance, 2) 
        
        if(distance<250 and distance>5): #To filter out junk values 
            right=distance
        else:
            right = dist1
        
        #print("right",right)

        time.sleep(0.1)

def leftsonar():
    global left
    while True:
        dist1=251
        GPIO.output(LEFTTRIG, True) 
        time.sleep(0.00001) 
        GPIO.output(LEFTTRIG, False) 
        echo_state=0 
        
        while echo_state == 0: 
            echo_state = GPIO.input(LEFTECHO) 
            pulse_start = time.time() 
        while GPIO.input(LEFTECHO)==1: 
            pulse_end = time.time() 
        pulse_duration = pulse_end - pulse_start 
        distance = pulse_duration * 17150 
        distance = round(distance, 2)
        
        if(distance<250 and distance>5): #To filter out junk values 
            left=distance
                
        else:
            left = dist1

        time.sleep(0.1)


def frontsonar():
    global front
    while True:
        dist1=251
        GPIO.output(FRONTTRIG, True) 
        time.sleep(0.00001) 
        GPIO.output(FRONTTRIG, False) 
        echo_state=0 
        
        while echo_state == 0: 
            echo_state = GPIO.input(FRONTECHO) 
            pulse_start = time.time() 
        while GPIO.input(FRONTECHO)==1: 
            pulse_end = time.time() 
        pulse_duration = pulse_end - pulse_start 
        distance = pulse_duration * 17150 
        distance = round(distance, 2) 
        
        if(distance<250 and distance>5): #To filter out junk values 
            front=distance
                            
        else:
            front = dist1
        #print("front",front)
        time.sleep(0.1)

        

def backsonar():
    global back
    while True:
        dist1=251
        GPIO.output(BACKTRIG, True) 
        time.sleep(0.00001) 
        GPIO.output(BACKTRIG, False) 
        echo_state=0 
        
        while echo_state == 0: 
            echo_state = GPIO.input(BACKECHO) 
            pulse_start = time.time() 
        while GPIO.input(BACKECHO)==1: 
            pulse_end = time.time() 
        pulse_duration = pulse_end - pulse_start 
        distance = pulse_duration * 17150 
        distance = round(distance, 2)
        
        if(distance<250 and distance>5): #To filter out junk values 
            back=distance
                
        else:
            back = dist1
        
        #print("back",back)
        time.sleep(0.1)




Thread(target = rightsonar).start()
Thread(target = leftsonar).start()
Thread(target = frontsonar).start()
Thread(target = backsonar).start()
#Thread(target = send_distance_message).start()

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
point1 = LocationGlobalRelative(float(latt),float(long), alt)
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)
vehicle.simple_goto(point1)
while True:
    send_distance_message()
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        #time.sleep(1)
        break
    time.sleep(0.3)
vehicle.mode = VehicleMode("LAND")
while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    # Break and return from function just below target altitude.
    if vehicle.location.global_relative_frame.alt <=0:
        print("Reached ground")
        vehicle.close() 
        break
    time.sleep(1)