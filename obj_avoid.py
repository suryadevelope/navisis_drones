from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import RPi.GPIO as GPIO 
from threading import Thread
import math
import multiprocessing

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

obstacledist = 70
vehicleheading = 0

RIGHTTRIG = 18  # Trigger pin of the Ultrasonic Sensor 
RIGHTECHO = 23 #Echo pin of the Ultrasonic Sensor

LEFTTRIG = 24
LEFTECHO = 25

FRONTTRIG = 4
FRONTECHO = 17

BACKTRIG = 27
BACKECHO = 22

sonardist ={}
# sonardist["right"] = 300
# sonardist["left"] = 300
# sonardist["front"] = 300
# sonardist["back"] = 300

right = 300
left = 300
front = 300
back = 300



GPIO.setup(RIGHTTRIG,GPIO.OUT) 
GPIO.setup(RIGHTECHO,GPIO.IN) 
GPIO.setup(LEFTTRIG,GPIO.OUT) 
GPIO.setup(LEFTECHO,GPIO.IN) 
GPIO.setup(FRONTTRIG,GPIO.OUT) 
GPIO.setup(FRONTECHO,GPIO.IN) 
GPIO.setup(BACKTRIG,GPIO.OUT) 
GPIO.setup(BACKECHO,GPIO.IN) 


def send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration=0):
    global distanceToTargetLocation
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame Needs to be MAV_FRAME_BODY_OFFSET_NED for forward/back left/right control.
        0b0000111111000111, # type_mask
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # m/s
        0, 0, 0, # x, y, z acceleration
        int(vehicleheading), 0)
    print(msg)
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        if x == duration-1:
            time.sleep(duration)
            point1 = LocationGlobalRelative(float(latt),float(long), takeoff_alt)
            distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)

            vehicle.parameters["WPNAV_SPEED"]=100
            vehicle.groundspeed=5
            time.sleep(1)
            vehicle.simple_goto(point1)
        time.sleep(1)

def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5

connection_string = "/dev/ttyAMA0"#args.connect

takeoff_alt = 1.5
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
latt = "17.461851"
long = "78.59291"
vehicle.airspeed = 5
vehicle.groundspeed = 50
vehicle.parameters['LAND_SPEED'] = 40 ##Descent speed of 30cm/s
vehicle.parameters["WPNAV_SPEED"]=100
vehicleheading = vehicle.heading

def arm_drone():
    while not vehicle.is_armable:
        time.sleep(1)
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        print('Waiting for arming...')
        time.sleep(1)
    vehicle.simple_takeoff(takeoff_alt) # Take off to target altitude
    while True:
        print('Altitude: %d' %  vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= takeoff_alt * 0.95:
            print('REACHED TARGET ALTITUDE')
            break
        time.sleep(1)


# This is the command to move the copter 5 m/s forward for 10 sec.
# velocity_x = 0
# velocity_y = 5
# velocity_z = 0
# duration = 10
# send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)

# backwards at 5 m/s for 10 sec

def rightsonar(): 
    global right
    while True:
        dist1=250 
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
        time.sleep(0.4)

def leftsonar():
    global left
    while True:
        dist1=250 
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
        #print("left",left)
        time.sleep(0.4)

 
def frontsonar():
    global front
    while True:
        
        dist1=250 
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
        time.sleep(0.4)

        

def backsonar():
    global back
    while True:
        dist1=250 
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
        time.sleep(0.4)


def objavoid():
    while True:
        # print("========================================")
        # print("sonar front",front)
        # print("sonar back",back)
        # print("sonar right",right)
        # print("sonar left",left)
        # print("*****************************************")
        if vehicle.location.global_relative_frame.alt >= takeoff_alt * 0.95:
            if (front<=obstacledist):
                if (right>obstacledist):
                    print("obstacle front go right")
                    velocity_x = 0
                    velocity_y = 1
                    velocity_z = 0
                    duration = 1
                    send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                elif (left>obstacledist):
                    print("obstacle front and right go left")
                    velocity_x = 0
                    velocity_y = -1
                    velocity_z = 0
                    duration = 1
                    send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                elif (right<=obstacledist) and (left<=obstacledist):
                    print("front,right and left obstacle go back ")
                    velocity_x = -1
                    velocity_y = 0
                    velocity_z = 0
                    duration = 1
                    #takeoff_alt = takeoff_alt+velocity_z*duration
                    send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                    #time.sleep(2)

                
            else:
                print("no obstacle")

                time.sleep(1)

# multiprocessing.Process(target=rightsonar, args=()).run()
# multiprocessing.Process(target=leftsonar, args=()).run()
# multiprocessing.Process(target=frontsonar, args=()).run()
# multiprocessing.Process(target=backsonar, args=()).run()
# multiprocessing.Process(target=objavoid, args=()).run()

Thread(target = rightsonar).start()
Thread(target = leftsonar).start()
Thread(target = frontsonar).start()
Thread(target = backsonar).start()
Thread(target = objavoid).start()

arm_drone()
time.sleep(2)
print("Vehicle going to the location")
point1 = LocationGlobalRelative(float(latt),float(long), takeoff_alt)
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)
vehicle.simple_goto(point1)
checkheading = 0
while True:
   

    vehicleheading = vehicle.heading   
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    if checkheading==0:
        vehicleheading = vehicle.heading
        checkheading = 1
    #print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        time.sleep(2)
        break
           
    time.sleep(2)


vehicle.mode = VehicleMode("LAND")
while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    # Break and return from function just below target altitude.
    if vehicle.location.global_relative_frame.alt <=0.55:
        print("Reached ground")
        vehicle.close() 
        break
    time.sleep(1)

