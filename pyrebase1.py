from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import pyrebase


# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
print(args.connect)

connection_string = "/dev/ttyAMA0"#args.connect
print('args :', args.connect)

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



# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, baud=921600)
while True:
       db.child("battery").set(str(vehicle.battery))
       print('Battery percentage : %s' % vehicle.battery)
       time.sleep(2)





