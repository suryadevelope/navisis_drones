

# import time
# from tfmini import TFmini

# # create the sensor and give it a port and (optional) operating mode
# tf = TFmini('/dev/ttyAMA0', mode=TFmini.STD_MODE)

# try:
#     print('='*25)
#     while True:
#         d = tf.read()
#         if d:
#             print(f'Distance: {d:5}')
#         else:
#             print('No valid response')
#         time.sleep(0.1)

# except KeyboardInterrupt:
#     tf.close()
#     print('bye!!')

# -*- coding: utf-8 -*
import pigpio
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
from threading import Thread


RX = 23

pi = pigpio.pi()
#pi.bb_serial_read_close(RX)
#pi.stop()q

pi.set_mode(RX, pigpio.INPUT)
pi.bb_serial_read_open(RX, 115200) 

stop = False


milliseconds=0

#Connects to the vehicle using serial port. 
print('Connecting to vehicle on: %s' % "/dev/ttyAMA0")
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=921600) #Function to convert distance and orientation into a mavlink message 
#vehicle.wait_ready(True, raise_exception=False)

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
              if vehicle.location.global_relative_frame.alt >= 0.5 * 0.95:
                 sensor_data(distance,4)
            # else:
            #   raise ValueError('distance error: %d' % distance)	
            # i = i + 9


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
          pi.bb_serial_read_close(RX)
          pi.stop()
        
  Thread(target = ultra).start()
  
  print("vehicle started ")
 
  #arm_and_takeoff(1.5)