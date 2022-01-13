

import pigpio
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from threading import Thread
import math
import datetime
from pymavlink.dialects.v20 import ardupilotmega as mavlink2



latt = "17.461773"
long = "78.592902"
alt = 1.5

RX = 6

pi = pigpio.pi()

def pigpiodsetup():
  pi = pigpio.pi()
  pi.set_mode(RX, pigpio.INPUT)
  pi.bb_serial_read_open(RX, 115200) 

try:
  pigpiodsetup()
except Exception as e:
  print("surya",e,str(e)=="'GPIO already in use'")
  if str(e)== "'GPIO already in use'":
      pi.bb_serial_read_close(RX)
      pi.stop()
      time.sleep(2)
      pigpiodsetup()
      print(e)


stop = False


milliseconds=0

#Connects to the vehicle using serial port. 
print('Connecting to vehicle on: %s' % "/dev/ttyAMA0")
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=921600) #Function to convert distance and orientation into a mavlink message 
#vehicle.wait_ready(True, raise_exception=False)
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
UNIT16_MAX = 65535

def send_distance_message(front):
   
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
        28, #min distance
        250, #max distance
        15,#https://mavlink.io/en/messages/common.html#OBSTACLE_DISTANCE
        90,
        12
        )

    # msg = vehicle.message_factory.distance_sensor_encode(
    #     int(ts),          # time since system boot
    #     5,          # min distance cm
    #     300,      # max distance cm
    #     int(front),       # current distance, must be int
    #     0,          # type = laser?
    #     0,          # onboard id, not used
    #     1, #direction
    #     0           # covariance, not used
    # )
    time.sleep(0.1)
    if vehicle.location.global_relative_frame.alt  >= float(alt)-0.5:
        vehicle.send_mavlink(msg)
       
        print(msg)
        vehicle.flush()


def getTFminiData():
  while True:
   
    #time.sleep(0.05)	#change the value if needed
    (count, recv) = pi.bb_serial_read(RX)
    if count > 8:
      for i in range(0, count-9):
        if recv[i] == 89 and recv[i+1] == 89: # 0x59 is 89
          checksum = 0
          for j in range(0, 8):
            checksum = checksum + recv[i+j]
          checksum = checksum % 256
          if checksum == recv[i+8]:
            distance = recv[i+2] + recv[i+3] * 256
            strength = recv[i+4] + recv[i+5] * 256
            if distance <= 1200 and strength < 2000:
              print(distance, strength)
              if vehicle.location.global_relative_frame.alt >= float(alt)-0.5 :
                 send_distance_message(distance)
            


def arm_and_takeoff(aTargetAltitude):

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    # while not vehicle.is_armable:
    #     print(" Waiting for vehicle to initialise...")
    #     time.sleep(1)

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
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

if __name__ == '__main__':
    

  def ultra():
      try:
        print("trying")
        getTFminiData()
      except:  
          print("exception")
          pi = pigpio.pi()
          pi.bb_serial_read_close(RX)
          pi.stop()
          pigpiodsetup()
          print(e)
        
  Thread(target = ultra).start()
  
  print("vehicle started ")
 
def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5


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
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        #time.sleep(1)
        break
    time.sleep(2)

vehicle.mode = VehicleMode("LAND")
while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    # Break and return from function just below target altitude.
    if vehicle.location.global_relative_frame.alt <=0:
        print("Reached ground")
        vehicle.close() 
        break
    time.sleep(1)