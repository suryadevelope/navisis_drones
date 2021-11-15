
import pyzbar.pyzbar as pyzbar
import cv2
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal
import numpy as np
import argparse
import math
import time
from os import sys, path
from threading import Thread

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


latt = "17.461703"
long = "78.592935"
alt = 2

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='')
args = parser.parse_args()
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

# --------------------------------------------------
#-------------- FUNCTIONS
# --------------------------------------------------


def get_location_metres(original_location, dNorth, dEast):

    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    print("dlat, dlon", dLat, dLon)

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return(newlat, newlon)


def marker_position_to_angle(x, y, z):

    angle_x = math.atan2(x, z)
    angle_y = math.atan2(y, z)

    return (angle_x, angle_y)


def camera_to_uav(x_cam, y_cam):  # unmanned areial vehicle
    x_uav = -y_cam
    y_uav = x_cam
    return(x_uav, y_uav)


def uav_to_ne(x_uav, y_uav, yaw_rad):
    c = math.cos(yaw_rad)
    s = math.sin(yaw_rad)

    north = x_uav*c - y_uav*s
    east = x_uav*s + y_uav*c
    return(north, east)


def check_angle_descend(angle_x, angle_y, angle_desc):
    return(math.sqrt(angle_x**2 + angle_y**2) <= angle_desc)


# --------------------------------------------------
#-------------- CONNECTION
# --------------------------------------------------
# -- Connect to the vehicle
print('Connecting...')
connection_string = "/dev/ttyAMA0"  # args.connect


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, timeout=60, baud=921600)
print('Connected to vehicle on port: %s' % connection_string)

# --------------------------------------------------
#-------------- PARAMETERS
# --------------------------------------------------

targetstatus = 0
rad_2_deg = 180.0/math.pi
deg_2_rad = 1.0/rad_2_deg

# --------------------------------------------------
# -------------- LANDING MARKER
# --------------------------------------------------
# --- Define Tag
id_to_find = 72
marker_size = 10  # - [cm]
freq_send = 1  # - Hz

land_alt_cm = 50.0
angle_descend = 20*deg_2_rad
land_speed_cms = 30.0


time_0 = time.time()


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




def campare():
    while True:

        # get the image
        print("loop started")
        _, img = cap.read()
        # get bounding box coords and data
        data, bbox, _ = detector.detectAndDecode(img)
        decodedObjects = pyzbar.decode(img)

        for decodedObject in decodedObjects:
            points = decodedObject.polygon
            left = decodedObject.rect[0]
            top = decodedObject.rect[1]
            height = decodedObject.rect[3]
            width = decodedObject.rect[2]

            # If the points do not form a quad, find convex hull
            if len(points) > 4:
                hull = cv2.convexHull(
                    np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else:
                hull = points

            # Number of points in the convex hull
            n = len(hull)

            # Draw the convext hull
            for j in range(0, n):
                cv2.line(cv2.IMREAD_LOAD_GDAL, hull[j], hull[(j+1) % n], (255, 0, 0), 3)

            ymin = (int(top))
            xmin = (int(left))
            print(ymin, xmin)

            x_cm, y_cm = camera_to_uav(xmin/100, ymin/100)
            uav_location = vehicle.location.global_relative_frame

            if uav_location.alt >= alt:
                if targetstatus == 1:
                    if data == "surya":
                        z_cm = uav_location.alt*100.0
                        angle_x, angle_y = marker_position_to_angle(x_cm, y_cm, z_cm)

                        if time.time() >= time_0 + 1.0/freq_send:
                            time_0 = time.time()
                            # print ""
                            print(" ")
                            print("Altitude = %.0fcm" % z_cm)
                            print("Marker found x = %5.0f cm  y = %5.0f cm -> angle_x = %5f  angle_y = %5f" %
                                (x_cm, y_cm, angle_x*rad_2_deg, angle_y*rad_2_deg))

                            north, east = uav_to_ne(x_cm, y_cm, vehicle.attitude.yaw)
                            print("Marker N = %5.0f cm   E = %5.0f cm   Yaw = %.0f deg" % (
                                north, east, vehicle.attitude.yaw*rad_2_deg))

                            marker_lat, marker_lon = get_location_metres(uav_location, north*0.01, east*0.01)
                            marker_lat = float(f'{float(marker_lat):.6f}')
                            marker_lon = float(f'{float(marker_lon):.6f}')
                            # -- If angle is good, descend
                            if check_angle_descend(angle_x, angle_y, angle_descend):
                                print("Low error: descending")
                                location_marker = LocationGlobalRelative(marker_lat, marker_lon, uav_location.alt-(land_speed_cms*0.01/freq_send))
                            else:
                                location_marker = LocationGlobalRelative(marker_lat, marker_lon, uav_location.alt)
                            vehicle.mode = VehicleMode("GUIDED")
                            vehicle.simple_goto(location_marker)
                            print("UAV Location    Lat = %.7f  Lon = %.7f" %(uav_location.lat, uav_location.lon))
                            print("Commanding to   Lat = %.7f  Lon = %.7f" %(location_marker.lat, location_marker.lon))
                            
                            print("status : ",str(str(vehicle.location.global_frame.lat)+","+str(vehicle.location.global_frame.lon)) >= str(str(location_marker.lat)+","+str(location_marker.lon)))
                            
                            if (str(str(vehicle.location.global_frame.lat)+","+str(vehicle.location.global_frame.lon)) >= str(str(location_marker.lat)+","+str(location_marker.lon))):
                                print("Reached target qrcode location")
                                print(" -->>COMMANDING TO LAND<<")
                                vehicle.mode = VehicleMode("LAND")
                                while True:
                                    print(" Altitude: ", vehicle.location.global_relative_frame.alt)
                                    # Break and return from function just below target altitude.
                                    if vehicle.location.global_relative_frame.alt <=0:
                                        print("Reached ground")
                                        targetstatus = 0
                                        break
                                    time.sleep(1)
                                
                                if vehicle.location.global_relative_frame.alt <=0:
                                    vehicle.close()
                                    break
                                break

        cv2.imshow("code detector", img)
        if(cv2.waitKey(1) == ord("q")):
            break
    # free camera object and exit
    cap.release()
    cv2.destroyAllWindows()


def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5



vehicle.parameters["WPNAV_SPEED"]=100
vehicle.parameters['PLND_ENABLED'] = 1
vehicle.parameters['PLND_TYPE'] = 1 ##1 for companion computer
vehicle.parameters['PLND_EST_TYPE'] = 0 ##0 for raw sensor, 1 for kalman filter pos estimation
vehicle.parameters['LAND_SPEED'] = 5 ##Descent speed of 30cm/s
#vehicle.mode = VehicleMode("LOITER")
Thread(target = campare).start()

time.sleep(5)
arm_and_takeoff(alt)

time.sleep(1)
print("Vehicle going to the location")
point1 = LocationGlobalRelative(float(latt),float(long), alt)
distanceToTargetLocation = get_distance_meters(point1,vehicle.location.global_relative_frame)
vehicle.simple_goto(point1)
while True:
    
    currentDistance = get_distance_meters(point1,vehicle.location.global_relative_frame)
    print("current distance: ", currentDistance,distanceToTargetLocation*.02,currentDistance<distanceToTargetLocation*.02)
    if currentDistance<distanceToTargetLocation*.02:
        print("Reached target location.")
        targetstatus = 1
        time.sleep(2)
        break
           
    time.sleep(3)