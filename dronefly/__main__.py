
import cloud
from dronekit import connect, VehicleMode, LocationGlobalRelative
import vehicleinfo
import time

print('Connecting to vehicle on: /dev/ttyAMA0' )
vehicle = connect("/dev/ttyAMA0", wait_ready=True, baud=921600)
vehicle.wait_ready(True, raise_exception=False)


vehicle.airspeed = 5
vehicle.groundspeed = 50
vehicle.parameters['LAND_SPEED'] = 40 ##Descent speed of 30cm/s
vehicle.parameters["WPNAV_SPEED"]=200

# #Create a message listener using the decorator.
# @vehicle.on_message('*')
# def listener(self, name, message):
#     print(message)


vinfo = vehicleinfo.info(vehicle)
cloud.__cloudupload("dinfo",vinfo)
cloudd = cloud.Cloudint()
clouddata = {}
clouddata["ddl"]={}
clouddata['alt'] = cloudd[0]
clouddata['dcl'] = cloudd[1]
clouddata['ddl']["lat"] = cloudd[2].split(",")[0]
clouddata['ddl']["lng"] = cloudd[2].split(",")[1]
clouddata['dinfo'] = cloudd[3]
clouddata['drive'] = cloudd[4]

def vehicle_goto(lat,long,alt):
    print("Take off complete")
    # Hover for 10 seconds
    time.sleep(3)
    print("Vehicle going to the location")
    point1 = LocationGlobalRelative(float(lat),float(long), alt)
    distanceToTargetLocation = vehicleinfo.get_distance_meters(point1,vehicle.location.global_relative_frame)
    vehicle.simple_goto(point1)

    while True:        
        currentDistance = vehicleinfo.get_distance_meters(point1,vehicle.location.global_relative_frame)
        print("current distance: ", currentDistance,distanceToTargetLocation*.05,currentDistance<distanceToTargetLocation*.05)
        print("time",currentDistance/2)
        string = str(vehicle.location.global_relative_frame.lat)+","+str(vehicle.location.global_relative_frame.lon)
        cloud.__cloudupload("dcl",string+","+str(currentDistance)+","+str(distanceToTargetLocation))
        
        if currentDistance<=distanceToTargetLocation*.05:
            print("Reached target location.")
            vehicleinfo.vehicle_Land(vehicle,VehicleMode)
            time.sleep(2)
            break
            
        time.sleep(3)

def vehiclestart():
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
        
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                vehicle_goto(clouddata['ddl']['lat'],clouddata['ddl']['lng'],aTargetAltitude)
                break
            time.sleep(1)
    point11 = LocationGlobalRelative(float(clouddata['ddl']['lat']),float(clouddata['ddl']['lng']), clouddata['alt'])
    distanceToTargetLocation1 = vehicleinfo.get_distance_meters(point11,vehicle.location.global_relative_frame)
    if(distanceToTargetLocation1<=1):
        cloud.__cloudupload("drive",0)
        cloud.__cloudupload("device_error",[400,"Distance to location is below 1 meter"])
        return
    arm_and_takeoff(float(clouddata['alt']))
    

def __updatefromcloud(type,data):# This function important for cloud onchange
   
    if type == "drive":
            clouddata["drive"] = data

    if clouddata["drive"] == 0:
        if type == "alt":
            clouddata["alt"] = data
        elif type == "dcl":
            clouddata["dcl"] = data
        elif type == "ddl":
            clouddata['ddl']["lat"] = data.split(",")[0]
            clouddata['ddl']["lng"] = data.split(",")[1]
        elif type == "dinfo":
            clouddata["dinfo"] = data
    if type == "drive":
        if data == 1:
            vehiclestart()

    print(clouddata['ddl']['lat'])