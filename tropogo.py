import requests
from dronekit import connect, VehicleMode, LocationGlobalRelative
from datetime import datetime
import pyrebase
import json


firebaseConfig = {
  "apiKey": "AIzaSyC8746CnMiMlKXVE40PmbuHQuRZ-uuTZuE",
  "authDomain": "artificial-intelligence-drone.firebaseapp.com",
  "databaseURL": "https://artificial-intelligence-drone-default-rtdb.firebaseio.com",
  "projectId": "artificial-intelligence-drone",
  "storageBucket": "artificial-intelligence-drone.appspot.com",
  "messagingSenderId": "606747160720",
  "appId": "1:606747160720:web:82f34e41b053b5d670a815",
  "measurementId": "G-KD6478D5PC"
};

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Today's date:", today)


connection_string = "/dev/ttyAMA0"#args.connect

print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
vehicle.wait_ready(True, raise_exception=False)

while True:
    response = requests.get('https://swatapi.tropogo.com/assets/location/nearest/?lat='+str(vehicle.location.global_frame.lat)+'&lng='+str(vehicle.location.global_frame.lon)+'&select_time_date='+str(today)+'&distance=10')
    response.raise_for_status()

    data = response.json()

    print(data)
    if data['restricted'] == False:
        print("you are in safe zone to fly")
        db.child("tropogo/status").set(str("false"))
        db.child("tropogo/zone").set(str(data['zone']))
        
        json.dumps(data, separators=(',', ':'))
        print(data)
        db.child("tropogo/data").set(str("true"))
    else:
        print("You are restricted to fly here")
        db.child("tropogo/status").set(str("false"))
        db.child("tropogo/zone").set(str(data['zone']))
        
        del data['restricted']
        del data['zone']
        print(json.dumps(data, separators=(',', ':')))
        db.child("tropogo/data").set(str(json.dumps(data, separators=(',', ':'))))
    
    
    