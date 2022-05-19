import math

import cv2
import numpy as np
from dronekit import VehicleMode, connect
import time

#color settings
hue_lower = 55
hue_upper = 185
saturation_lower = 110
saturation_upper = 170
value_lower = 190
value_upper = 250
min_contour_area = 500 # the smallest number of pixels in a contour before it will register this as a target

#camera
horizontal_fov = 118.2 * math.pi/180
vertical_fov = 69.5 * math.pi/180
horizontal_resolution = 1280
vertical_resolution = 720
connection_string = "/dev/ttyAMA0"  # args.connect
vehicle = connect(connection_string, wait_ready=True, timeout=60, baud=921600)


def send_land_message(x, y):
    msg = vehicle.message_factory.landing_target_encode(
        0,       # time_boot_ms (not used)
        0,       # target num
        0,       # frame
        (x-horizontal_resolution/2)*horizontal_fov/horizontal_resolution,
        (y-vertical_resolution/2)*vertical_fov/vertical_resolution,
        0,       # altitude.  Not supported.
        0,0)     # size of target in radians
    vehicle.send_mavlink(msg)
    vehicle.flush()




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

arm_and_takeoff(1);