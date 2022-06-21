import __main__

import pyrebase
from dronekit import connect, VehicleMode, LocationGlobalRelative
from getmac import get_mac_address
# Python Imports
import time
import stream

import vehicleinfo
from datetime import datetime


import json

dictionary ={}

def writetofile(dir1):
    with open("dronefly/cred.json", "w") as outfile:
        jsonString = json.dumps(dictionary)
        outfile.write(jsonString)
        outfile.close()


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
    QRid = db.child("device/"+macaddress+"/id").get().val()
    vconnect = db.child("device/"+macaddress+"/vconnect").get().val()
    vrtlmode = db.child("device/"+macaddress+"/rtl").get().val()

    if daltitude == None:
        db.child("device/"+macaddress+"/altitude").set("0")
        db.child("device/"+macaddress+"/dcl").set("0,0")
        db.child("device/"+macaddress+"/ddl").set("0,0")
        db.child("device/"+macaddress+"/dinfo").set("null")
        db.child("device/"+macaddress+"/drive").set(0)
        db.child("device/"+macaddress+"/Dstatus").set(["ONLINE",formatted_time_in_utc])
        db.child("device/"+macaddress+"/id").set("null")
        db.child("device/"+macaddress+"/vconnect").set(0)
        db.child("device/"+macaddress+"/rtl").set(0)
        dictionary["altitude"] = "0"
        dictionary["dcl"] = "0,0"
        dictionary["ddl"] = "0,0"
        dictionary["dinfo"] = "null"
        dictionary["drive"] = 0
        dictionary["id"] = "null"
        dictionary["vconnect"] = 0
        dictionary["rtl"] = 0
        dictionary["Dstatus"] = ["ONLINE",formatted_time_in_utc]
        time.sleep(0.2)
    else:
        dictionary["altitude"] = daltitude
        dictionary["dcl"] = dcl
        dictionary["ddl"] = ddl
        dictionary["dinfo"] = dinfo
        dictionary["drive"] = ddrive
        dictionary["id"] = QRid
        dictionary["vrtl"] = vrtlmode
        dictionary["vconnect"] = vconnect
        dictionary["Dstatus"] = Dstatus

    if int(vconnect)==1:
        db.child("device/"+macaddress+"/vconnect").set(0)
        vconnect = 0
        dictionary["vconnect"] = vconnect

    if int(ddrive )== 1:
        db.child("device/"+macaddress+"/drive").set(0)
        ddrive = 0
        dictionary["drive"] = ddrive

    if int(vrtlmode) == 1:
        db.child("device/"+macaddress+"/rtl").set(0)
        dictionary["vrtl"] = 0


    time.sleep(1)
    if str(Dstatus[0]) == "OFFLINE":
        db.child("device/"+macaddress+"/Dstatus").set(["ONLINE",formatted_time_in_utc])
        Dstatus[0] = "ONLINE"
        Dstatus[1] = formatted_time_in_utc
        dictionary["Dstatus"] = Dstatus
        time.sleep(0.2)
        

    if daltitude != None:
       
        def stream_handler(message):
            # print(message["event"]) # put
            print(message["path"]) # /-K7yGTTEp7O549EzTYtI
            # print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
            
            if ignorecloud["status"] == 0:
                if message["path"] == "/altitude":
                    daltitude = message["data"]
                    dictionary["altitude"] = daltitude

                # elif message["path"] == "/dcl":
                #     dcl = message["data"]
                #     __main__.__updatefromcloud("dcl",dcl)
                elif message["path"] == "/ddl":
                    ddl = message["data"]
                    dictionary["ddl"] = ddl

                # elif message["path"] == "/dinfo":
                #     dinfo = message["data"]
                #     __main__.__updatefromcloud("dinfo",dinfo)
                elif message["path"] == "/drive":
                    ddrive = message["data"]
                    dictionary["drive"] = ddrive

                elif message["path"] == "/id":
                    qrcodeid = message["data"]
                    dictionary["id"] = qrcodeid
                elif message["path"] == "/rtl":
                    vrtlmode = message["data"]
                    dictionary["vrtl"] = vrtlmode

                elif message["path"] == "/Dstatus/0":
                    Dstatus = message["data"]
                    if str(Dstatus) == "OFFLINE":
                        __cloudupload("Dstatus",["ONLINE",formatted_time_in_utc])
                    dictionary["Dstatus"] = ["ONLINE",formatted_time_in_utc]

                elif message["path"] == "/vconnect":
                    vconnect = message["data"]
                    if int(vconnect) == 0:
                        __cloudupload("vconnect",1)
                        dictionary["vconnect"] = 1

                writetofile(dictionary)                

            else:
                ignorecloud["status"]=0
                dictionary["status"] = 0

                writetofile(dictionary)
            
        my_stream = db.child("device/"+macaddress).stream(stream_handler)
    stream.streamfetchdata("cloudqrid",QRid)
    writetofile(dictionary)
    return [daltitude,dcl,ddl,ddrive,QRid,vrtlmode]

    ############################INIT DEVICE#####################################

def __cloudupload(path,data):
    if firebase:
        ignorecloud["status"] = 1
        db.child("device/"+macaddress+"/"+path).set(data)
        dictionary[path] = data
        writetofile(dictionary)
        ignorecloud["status"] = 0
        time.sleep(2)