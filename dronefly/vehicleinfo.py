
import math
import time
import cloud


vehicledata = {"QRCODEDATA":"null"}
def vdatafetch(condition,value):
    vehicledata[condition]=value

def info(vehicle):

    s = {"APMV":str(vehicle.version),
        "type":vehicle.version.release_type(),
        "ReleaseV":vehicle.version.release_version(),
        "Stable":vehicle.version.is_stable(),
        "MISSION_FLOAT":vehicle.capabilities.mission_float,
        "PARAM_FLOAT":vehicle.capabilities.param_float,
        "MISSION_INT":vehicle.capabilities.mission_int,
        "COMMAND_INT":vehicle.capabilities.command_int,
        "PARAM_UNION" : vehicle.capabilities.param_union,
        "FTPenable":vehicle.capabilities.ftp,
        "attitude_offboard_CMD":vehicle.capabilities.set_attitude_target,
        "set_attitude_target_local_ned":vehicle.capabilities.set_attitude_target_local_ned,
        "set_altitude_target_global_int":vehicle.capabilities.set_altitude_target_global_int,
        "terrain_protocol":vehicle.capabilities.terrain,
        "set_actuator_target":vehicle.capabilities.set_actuator_target,
        "flight_termination":vehicle.capabilities.flight_termination,
        "mission_float": vehicle.capabilities.mission_float,
        "compass_calibration":vehicle.capabilities.compass_calibration,
        "Global_Location":str(vehicle.location.global_frame),
        "global_relative_frame":str(vehicle.location.global_relative_frame),
        "Local_Location":str(vehicle.location.local_frame),
        "Attitude":str(vehicle.attitude),
        "Velocity":vehicle.velocity,
        "GPS:":str(vehicle.gps_0),
        "Gimbal_status":str(vehicle.gimbal),
        "Battery":str(vehicle.battery),
        "EKF_OK":vehicle.ekf_ok,
        "Last_Heartbeat":vehicle.last_heartbeat,
        "Rangefinder":str(vehicle.rangefinder),
        "RangefinderD":vehicle.rangefinder.distance,
        "RangefinderV": vehicle.rangefinder.voltage,
        "Heading" :vehicle.heading,
        "Is_Armable":vehicle.is_armable,
        "System_status":vehicle.system_status.state,
        "Groundspeed":vehicle.groundspeed,
        "Airspeed":vehicle.airspeed,  
        "Mode": vehicle.mode.name,    # settable
        "Armed": vehicle.armed    # settable

        }
    return s

def vrtl(vehicle):
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

def get_distance_meters(targetLocation,currentLocation):
    dLat=targetLocation.lat - currentLocation.lat
    dLon=targetLocation.lon - currentLocation.lon

    return math.sqrt((dLon*dLon)+(dLat*dLat))*1.113195e5

def vehicle_Land(vehicle,VehicleMode,qrcodeid):
    # while True:
    #     print("landing",str(vehicledata["QRCODEDATA"]) ,str(qrcodeid),str(vehicledata["QRCODEDATA"]) == str(qrcodeid))
    #     if str(vehicledata["QRCODEDATA"]) == str(qrcodeid):
    #         break;
    #     time.sleep(1)
    time.sleep(2)
    return True
    
    # vehicle.mode = VehicleMode("LAND")
    # while True:
    #     print("Landing Altitude: ", vehicle.location.global_relative_frame.alt*0.55)
    #     # Break and return from function just below target altitude.
    #     if vehicle.location.global_relative_frame.alt <=0.55:
    #         #cloud.__cloudupload("drive",0)
    #         vehicle.close() 
    #         break
    #     time.sleep(1)



