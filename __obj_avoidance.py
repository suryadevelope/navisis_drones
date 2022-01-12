from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import pigpio
from threading import Thread
import math

latt = "17.461794"
long = "78.5928"
alt = 15.0

RX = 23
distanceToTargetLocation = 0
pi = pigpio.pi()

def pigpiodsetup():
  pi = pigpio.pi()

  pi.set_mode(RX, pigpio.INPUT)
  pi.bb_serial_read_open(RX, 115200) 

try:
  pigpiodsetup()
except Exception as e:
  if e == "GPIO already in use":
      pi = pigpio.pi()
      pi.bb_serial_read_close(RX)
      pi.stop()
      pigpiodsetup()
      print(e)



def getTFminiData():
      while True:
        time.sleep(0.05)	#change the value if needed
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
                  if vehicle.location.global_relative_frame.alt >= alt:
                      if distance <=400:
                        velocity_x = 0
                        velocity_y = -1
                        velocity_z = 0
                        duration = 1
                        
                        send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)
                        
                # else:
                #   raise ValueError('distance error: %d' % distance)	
                # i = i + 9



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
        print(x==duration,x,duration)
        time.sleep(duration)
        point1 = LocationGlobalRelative(float(latt),float(long), alt)
        distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)

        vehicle.parameters["WPNAV_SPEED"]=100
        vehicle.groundspeed=5
        time.sleep(2)
        vehicle.simple_goto(point1)
        time.sleep(1)

connection_string = "/dev/ttyAMA0"#args.connect

print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)


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
        #ultra()
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5



    

def ultra():
  try:
    print("trying")
    getTFminiData()
  except KeyboardInterrupt:  
      print("exception")
      pi.bb_serial_read_close(RX)
      pi.stop()
    
print("vehicle started ")

arm_and_takeoff(alt)

#Thread(target = ultra).start()
time.sleep(2)
print("Vehicle going to the location")
point1 = LocationGlobalRelative(float(latt),float(long), alt)
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)

vehicle.parameters["WPNAV_SPEED"]=300
vehicle.groundspeed=5
time.sleep(1)
vehicle.simple_goto(point1)

while True:
    #ultra()   
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        time.sleep(2)
        break
           
    time.sleep(0.1)

vehicle.groundspeed = 50
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

