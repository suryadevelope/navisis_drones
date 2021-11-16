from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import RPi.GPIO as GPIO 
from threading import Thread



GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 

obstacledist = 70

RIGHTTRIG = 18  # Trigger pin of the Ultrasonic Sensor 
RIGHTECHO = 23 #Echo pin of the Ultrasonic Sensor

LEFTTRIG = 24
LEFTECHO = 25

FRONTTRIG = 4
FRONTECHO = 17

BACKTRIG = 27
BACKECHO = 22

sonardist ={}
sonardist["right"] = -1
sonardist["left"] = -1
sonardist["front"] = -1
sonardist["back"] = -1

GPIO.setup(RIGHTTRIG,GPIO.OUT) 
GPIO.setup(RIGHTECHO,GPIO.IN) 
GPIO.setup(LEFTTRIG,GPIO.OUT) 
GPIO.setup(LEFTECHO,GPIO.IN) 
GPIO.setup(FRONTTRIG,GPIO.OUT) 
GPIO.setup(FRONTECHO,GPIO.IN) 
GPIO.setup(BACKTRIG,GPIO.OUT) 
GPIO.setup(BACKECHO,GPIO.IN) 


def send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration=0):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED, # frame Needs to be MAV_FRAME_BODY_NED for forward/back left/right control.
        0b0000111111000111, # type_mask
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # m/s
        0, 0, 0, # x, y, z acceleration
        0, 0)
    print(msg)
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

connection_string = "/dev/ttyAMA0"#args.connect

takeoff_alt = 1.5
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
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

#arm_drone()
# This is the command to move the copter 5 m/s forward for 10 sec.
# velocity_x = 0
# velocity_y = 5
# velocity_z = 0
# duration = 10
# send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)

# backwards at 5 m/s for 10 sec

time.sleep(2)
vehicle.parameters['LAND_SPEED'] = 40 ##Descent speed of 30cm/s

def rightsonar(): 
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
            sonardist["right"]=distance
            
        else:
            sonardist["right"] = 0 
        time.sleep(0.3)

def leftsonar():
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
            sonardist["left"]=distance
                
        else:
            sonardist["left"] = 0 
        time.sleep(0.3)

 
def frontsonar():
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
                sonardist["front"]=distance
                
        else:
            sonardist["front"] = 0 
        time.sleep(0.3)

def backsonar():
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
            sonardist["back"]=distance
                
        else:
            sonardist["back"] = 0 
        time.sleep(0.3)


Thread(target = rightsonar).start()
Thread(target = leftsonar).start()
Thread(target = frontsonar).start()
Thread(target = backsonar).start()

while True: 
    # print("started right",sonardist["right"])
    # print("started left",sonardist["left"])
    # print("started front",sonardist["front"])
    # print("started back",sonardist["back"])

    if (sonardist["front"]<=obstacledist):
        if (sonardist["right"]>obstacledist):
            print("obstacle front go right")
        elif (sonardist["left"]>obstacledist):
            print("obstacle front and right go left")
        else:
            print("front,right and left obstacle go up ")
    time.sleep(1)



