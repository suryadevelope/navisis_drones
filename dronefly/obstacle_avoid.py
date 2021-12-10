from pymavlink import mavutil
import time
import RPi.GPIO as GPIO 
from threading import Thread
 

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

obstacledata={}
obstacledata["ddl"]={}


def obstacledataupdate(alt,vehicleheading,latt,long):
    obstacledata['alt'] = alt
    obstacledata['vheading'] = vehicleheading
    obstacledata['ddl']["lat"] = latt
    obstacledata['ddl']["lng"] = long

def start_ObstacleScann(vehicle,alt,vehicleheading,latt,long,LocationGlobalRelative):
    obstacledata['alt'] = alt
    obstacledata['vheading'] = vehicleheading
    obstacledata['ddl']["lat"] = latt
    obstacledata['ddl']["lng"] = long

    def send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration=0):
       
        #global distanceToTargetLocation
        msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame Needs to be MAV_FRAME_BODY_OFFSET_NED for forward/back left/right control.
            0b0000001000000000,#0b0000111111000111, # type_mask
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # m/s
            0, 0, 0, # x, y, z acceleration
            int(obstacledata['vheading']), 20)
        print(msg)
        for x in range(0,duration):
            vehicle.send_mavlink(msg)
            if x == duration-1:
                time.sleep(duration)
                point1 = LocationGlobalRelative(float(obstacledata['ddl']["lat"]),float(obstacledata['ddl']["lng"]), float(obstacledata['alt']))
                time.sleep(1)
                vehicle.simple_goto(point1)
            time.sleep(1)




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
            global front
            global right
            global left
            global back
            if vehicle.location.global_relative_frame.alt >= float(obstacledata['alt']) * 0.95:
                if (front<=obstacledist):
                    if (right>obstacledist):
                        print("obstacle front go right")
                        velocity_x = 0
                        velocity_y = distance
                        velocity_z = 0
                        duration = distancespeed
                        right = 300
                        front = 300
                        send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                    elif (left>obstacledist):
                        print("obstacle front and right go left")
                        velocity_x = 0
                        velocity_y = -distance
                        velocity_z = 0
                        duration = distancespeed
                        right = 300
                        left = 300
                        front = 300
                        send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                    elif (right<=obstacledist) and (left<=obstacledist):
                        print("front,right and left obstacle go back ")
                        velocity_x = -distance
                        velocity_y = 0
                        velocity_z = 0
                        duration = distancespeed
                        right = 300
                        left = 300
                        front = 300
                        back = 300
                        #takeoff_alt = takeoff_alt+velocity_z*duration
                        send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                        #time.sleep(2)

                    
                else:
                    print("no obstacle")

                time.sleep(1)



    Thread(target = rightsonar).start()
    Thread(target = leftsonar).start()
    Thread(target = frontsonar).start()
    Thread(target = backsonar).start()
    Thread(target = objavoid).start()
