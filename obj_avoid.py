from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

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
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

connection_string = "/dev/ttyAMA0"#args.connect

takeoff_alt = 1.5
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
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

# backwards at 5 m/s for 10 sec.
velocity_x = 1
velocity_y = 0
velocity_z = 0
duration = 2
send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)

time.sleep(2)

velocity_x = 0
velocity_y = -1
velocity_z = 0
duration = 2
send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)

velocity_x = 1
velocity_y = 0
velocity_z = 0
duration = 3
send_body_ned_velocity(velocity_x, velocity_y, velocity_z, duration)

time.sleep(2)
vehicle.parameters['LAND_SPEED'] = 40 ##Descent speed of 30cm/s

vehicle.mode = VehicleMode("LAND")
while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
    # Break and return from function just below target altitude.
    if vehicle.location.global_relative_frame.alt <=0:
        print("Reached ground")
        vehicle.close() 
        break
    time.sleep(1)
