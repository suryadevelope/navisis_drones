from dronekit import connect, VehicleMode, LocationGlobalRelative
import vehicleinfo
import time
import stream
import sys
import obstacle_avoid
import cloud
from threading import Thread
import json
from json.decoder import JSONDecodeError
from jsondiff import diff
import numpy as np
import shortdist

cloud.__cloudupload("device_error", [200, "All OK AT INIT"])
vehicle = "null"
print('Connecting to vehicle on: /dev/ttyAMA0')
try:
    vehicle = connect("/dev/ttyAMA0", wait_ready=True, baud=921600)
    vehicle.wait_ready(True, raise_exception=False)
except:
    print("error connecting to vehicle")
    cloud.__cloudupload("vconnect", 0)
    cloud.__cloudupload("device_error", [
                        404, "Device connection error restart to fix, check supply or contact customer care"])
    sys.exit()

time.sleep(1)
cloudd = cloud.Cloudint()
time.sleep(2)
cloud.__cloudupload("vconnect", 1)
vehicle.airspeed = 5
time.sleep(0.2)
vehicle.groundspeed = 50
time.sleep(0.2)
print(vehicle)
vehicle.parameters['LAND_SPEED'] = 30  # Descent speed of 30cm/s
time.sleep(0.2)
vehicle.parameters["WPNAV_SPEED"] = 500
time.sleep(0.2)

finalformatedpointsarray = []
# #Create a message listener using the decorator.
# @vehicle.on_message('*')
# def listener(self, name, message):
#     print(message)


vinfo = vehicleinfo.info(vehicle)
cloud.__cloudupload("dinfo", vinfo)
streamurl = stream.startStream()
cloud.__cloudupload("streamurl", streamurl)


clouddata = {}
clouddata["ddl"] = {}
clouddata['alt'] = cloudd[0]
clouddata['dcl'] = cloudd[1]
clouddata['ddl'] = cloudd[2]
clouddata['drive'] = cloudd[3]
clouddata['qrid'] = cloudd[4]

print("ok surya")


def vehicle_goto(lat, long, alt,points,index):
    print("Take off complete")
    # Hover for 10 seconds
    time.sleep(3)
    print("Vehicle going to the location")
    point1 = LocationGlobalRelative(float(lat), float(long), alt)
    distanceToTargetLocation = vehicleinfo.get_distance_meters(
        point1, vehicle.location.global_relative_frame)
    vehicle.simple_goto(point1)
    checkheading = 0

    # obstacle_avoid.start_ObstacleScann(vehicle,clouddata['alt'],vehicle.heading,clouddata['ddl']["lat"],clouddata['ddl']["lng"],LocationGlobalRelative)
    while True:
        if checkheading <= 2:
            obstacle_avoid.obstacledataupdate(
                alt, vehicle.heading, float(lat), float(long),)
            checkheading = checkheading+1
        currentDistance = vehicleinfo.get_distance_meters(
            point1, vehicle.location.global_relative_frame)
        #print("current distance: ", currentDistance,distanceToTargetLocation*.05,currentDistance<distanceToTargetLocation*.05)
        # print("time",currentDistance/2)
        string = str(vehicle.location.global_relative_frame.lat) + \
            ","+str(vehicle.location.global_relative_frame.lon)
        cloud.__cloudupload(
            "dcl", string+","+str(currentDistance)+","+str(distanceToTargetLocation))

        if currentDistance <= distanceToTargetLocation*.05:
            print("Reached target location.")
            time.sleep(2)
            break

        time.sleep(2)

    if(index>=len(points)-1):

        vehicle.mode = VehicleMode("LAND")
        while True:
            print("Landing Altitude: ", vehicle.location.global_relative_frame.alt*0.55)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt <=0.55:
                cloud.__cloudupload("drive",0)
                vehicle.close() 
                break
            time.sleep(1)
    else:
        point1 = LocationGlobalRelative(float(lat), float(long), 1.5)
        vehicle.simple_goto(point1)
        
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt <= 2.5:
                print("Reached QR target altitude")
                break
            time.sleep(1)
        qrid = get_key(str(lat)+","+str(long))
        feed = vehicleinfo.vehicle_Land(vehicle, VehicleMode, qrid)
        while True:
            if(feed == True):
                print("wait for qr conformation")
                break

        point11 = LocationGlobalRelative(float(lat), float(long), float(clouddata['alt']))
        vehicle.simple_goto(point11)

        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= float(clouddata['alt']) * 0.95:
                print("Reached to normal target altitude")
                break
            time.sleep(1)
        i = index+1
        vehicle_goto(float(points[i][0].split(",")[0]), float(points[i][0].split(",")[1]), aTargetAltitude,points,i)



def vehiclestart(points,index):
    def arm_and_takeoff(aTargetAltitude,locpoints,i):

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
                vehicle_goto(float(locpoints[i][0].split(",")[0]), float(locpoints[i][0].split(",")[1]), aTargetAltitude,locpoints,i)
                break
            time.sleep(1)
    point11 = LocationGlobalRelative(float(points[index][0].split(",")[0]), float(points[index][0].split(",")[1]), clouddata['alt'])
    distanceToTargetLocation1 = vehicleinfo.get_distance_meters(
        point11, vehicle.location.global_relative_frame)
    if(distanceToTargetLocation1 <= 1):
        cloud.__cloudupload("drive", 0)
        cloud.__cloudupload(
            "device_error", [400, "Distance to location is below 1 meter"])
        return

    if float(vehicle.battery.voltage) >= 10.4:
        arm_and_takeoff(float(clouddata['alt']),points,index)
    else:
        cloud.__cloudupload(
            "device_error", [401, "Battery is lower than 10.5 volts"])
        cloud.__cloudupload("drive", 0)

def reorder(arr,index, n):
 
    temp = [0] * n;
 
    # arr[i] should be
        # present at index[i] index
    for i in range(0,n):
        temp[index[i]] = arr[i]
 
    # Copy temp[] to arr[]
    for i in range(0,n):
        arr[i] = temp[i]
        index[i] = i

def rearrangepoints(pointsarray):
    finalformatedpointsarray = []
    print(pointsarray.keys())
    for item in pointsarray.values():
        finalformatedpointsarray.append([float(item.split(",")[0]),float(item.split(",")[1])])
    finalformatedpointsarray.insert(len(pointsarray.values()),[vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon])
    sortindex = shortdist.driver(finalformatedpointsarray)
    np.array(finalformatedpointsarray)
    finalformatedpointsarray =[finalformatedpointsarray[i-1] for i in sortindex["path"]]


def get_key(val):
    for key, value in jsondata["ddl"].items():
         if val == value:
             return key
 
    return "key doesn't exist"


def __updatefromcloud():  # This function important for cloud onchange
    global jsondata
    jsondata = {}
    while True:
        time.sleep(0.5)
        with open('dronefly/cred.json', "r") as f:
            data = json.loads(f.read())
            if(type(data) == dict):
                if(diff(jsondata, data) != {}):
                    jsondata = data
            f.close()
        if(len(jsondata.keys()) > 0):
            clouddata["drive"] = jsondata["drive"]
            if int(clouddata["drive"]) == 0:
                clouddata["alt"] = jsondata["altitude"]
                clouddata["dcl"] = jsondata["dcl"]
                clouddata['ddl'] = jsondata["ddl"]
                clouddata["qrid"] = jsondata["id"]
                # print(clouddata)
                # stream.streamfetchdata("cloudqrid",clouddata["qrid"])
            elif int(clouddata["drive"]) == 1:
                rearrangepoints(clouddata["ddl"])

                vehiclestart(finalformatedpointsarray,0)
                # print(clouddata['ddl']['lat'])
            


Thread(target=__updatefromcloud).start()
