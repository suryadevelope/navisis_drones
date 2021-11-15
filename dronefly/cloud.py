
import pyrebase
from dronekit import connect, VehicleMode, LocationGlobalRelative
from getmac import get_mac_address
# Python Imports
import time

import __main__

from datetime import datetime


time_in_utc = datetime.utcnow()
formatted_time_in_utc = time_in_utc.strftime("%d/%m/%Y %H:%M:%S")

frame_count =0

macaddress = get_mac_address().upper()
print(macaddress)

firebaseConfig = {
  'apiKey': "AIzaSyC8746CnMiMlKXVE40PmbuHQuRZ-uuTZuE",
  'authDomain': "artificial-intelligence-drone.firebaseapp.com",
  'databaseURL': "https://artificial-intelligence-drone-default-rtdb.firebaseio.com",
  'projectId': "artificial-intelligence-drone",
  'storageBucket': "artificial-intelligence-drone.appspot.com",
  'messagingSenderId': "606747160720",
  'appId': "1:606747160720:web:4036e57927c8985a70a815",
  'measurementId': "G-0P2P00K5N0"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
ignorecloud = {}
ignorecloud["status"] = 0

def Cloudint():
 

    #retrive data

    
    daltitude = db.child("device/"+macaddress+"/altitude").get().val()
    dcl = db.child("device/"+macaddress+"/dcl").get().val()
    ddl = db.child("device/"+macaddress+"/ddl").get().val()
    dinfo = db.child("device/"+macaddress+"/dinfo").get().val()
    ddrive = db.child("device/"+macaddress+"/drive").get().val()
    Dstatus = db.child("device/"+macaddress+"/Dstatus").get().val()

    if daltitude == None:
        db.child("device/"+macaddress+"/altitude").set("0")
        db.child("device/"+macaddress+"/dcl").set("0,0")
        db.child("device/"+macaddress+"/ddl").set("0,0")
        db.child("device/"+macaddress+"/dinfo").set("null")
        db.child("device/"+macaddress+"/drive").set(0)
        db.child("device/"+macaddress+"/Dstatus").set(["ONLINE",formatted_time_in_utc])

    if int(ddrive )== 1:
        db.child("device/"+macaddress+"/drive").set(0)

    time.sleep(1)
    if str(Dstatus[0]) == "OFFLINE":
        db.child("device/"+macaddress+"/Dstatus").set(["ONLINE",formatted_time_in_utc])
        

    if daltitude != None:
       
        def stream_handler(message):
            # print(message["event"]) # put
            # print(message["path"]) # /-K7yGTTEp7O549EzTYtI
            # print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
            
            print(message["path"])
            if ignorecloud["status"] == 0:
                if message["path"] == "/altitude":
                    daltitude = message["data"]
                    __main__.__updatefromcloud("alt",daltitude)
                elif message["path"] == "/dcl":
                    dcl = message["data"]
                    __main__.__updatefromcloud("dcl",dcl)
                elif message["path"] == "/ddl":
                    ddl = message["data"]
                    __main__.__updatefromcloud("ddl",ddl)
                elif message["path"] == "/dinfo":
                    dinfo = message["data"]
                    __main__.__updatefromcloud("dinfo",dinfo)
                elif message["path"] == "/drive":
                    ddrive = message["data"]
                    __main__.__updatefromcloud("drive",ddrive)
                elif message["path"] == "/Dstatus/0":
                    Dstatus = message["data"]
                    if str(Dstatus) == "OFFLINE":
                        __cloudupload("Dstatus",["ONLINE",formatted_time_in_utc])
            else:
                ignorecloud["status"]=0
            

        my_stream = db.child("device/"+macaddress).stream(stream_handler)
    return [daltitude,dcl,ddl,dinfo,ddrive]

    ############################INIT DEVICE#####################################

def __cloudupload(path,data):
    if firebase:
        ignorecloud["status"] = 1
        db.child("device/"+macaddress+"/"+path).set(data)