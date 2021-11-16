import cv2
import numpy
from flask import Flask, render_template, Response, stream_with_context, request
import numpy as np
import requests
import json
from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode
import pyzbar.pyzbar as pyzbar
from threading import Thread
import time
import vehicleinfo

cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()
app = Flask('__name__')

streamexternaldata = {"cloudqrid":"null"}

def streamfetchdata(condition,val):
    streamexternaldata[condition]=val


def startStream():
    url = "https://api.remot3.it/apv/v27/device/connect"

    payload = {
    "deviceaddress":"80:00:00:00:01:1C:06:BE",
    "wait": "true",
    "hostip": "0.0.0.0"
    }


    content_length_header = str(len(json.dumps(payload)))
    key_id = "D7P5VZB6KJCISDNSARN4"
    key_secret_id = "D7f+jzFBmRJos75Q9B1iJdDEu6EiSWuMdFUQPgaI"
    auth1 =HTTPSignatureAuth(algorithm="hmac-sha256",
            key=b64decode(key_secret_id),
            key_id=key_id,
            headers=[
                '(request-target)', 'host',
                'date', 'content-type',
                'content-length'
            ])

    print(str(auth1))
    headers = {
    'path': "/apv/v27/device/connect",
    'host': 'api.remot3.it',
    'content-type': 'application/json',
        'content-length': content_length_header,
        "developerkey":"N0JGMjU3QUItRjA2Qy00QzJDLUEyNUEtMTU2QjkxRjE1QkEw"
    }
    response = requests.post(url,auth=auth1,json=payload, headers=headers)

    print(json.loads(response.text)["connection"]["proxy"],"/video")
    if json.loads(response.text)["connection"]:
        return json.loads(response.text)["connection"]["proxy"]+"/video"

ret,img = "null","null"

def camerastream():
    while True:
        # get bounding box coords and data
        ret,img = cap.read()
        if not ret:
            break;
        else:
        
            data, bbox, _ = detector.detectAndDecode(img)
            decodedObjects = pyzbar.decode(img)

            for decodedObject in decodedObjects:
                points = decodedObject.polygon
                left = decodedObject.rect[0]
                top = decodedObject.rect[1]
                height = decodedObject.rect[3]
                width = decodedObject.rect[2]
                data = decodedObject.data
                vehicleinfo.vdatafetch("QRCODEDATA",data.decode())
                points = decodedObject.polygon
                if data.decode() == streamexternaldata["cloudqrid"]:
                    if len(points) > 4:
                        hull = cv2.convexHull(
                            np.array([points for point in points], dtype=np.float32))
                        hull = list(map(tuple, np.squeeze(hull)))
                    else:
                        hull = points

                    n = len(hull)
                    # draw the lines on the QR code 
                    for j in range(0, n):
                        # print(j, "      ", (j + 1) % n, "    ", n)

                        cv2.line(img, hull[j], hull[(j + 1) % n], (0, 255, 0), 2)
                    # finding width of QR code in the image 
                    x, x1 = hull[0][0], hull[1][0]
                    y, y1 = hull[0][1], hull[1][1]
                    
                    Pos = hull[3]

                    #print(data)
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

                    ymin = (int(top+(height/2)))/100.0
                    xmin = (int(left+(width/2)))/100.0
                    print(ymin, xmin)
                    
                    cv2.circle(img,(int(left+(width/2)),int(top+(height/2))),5,(255,0,0),-1)
                
                    break      
                            
                            
            cv2.imshow("QRCODE SCREEN", img)
            if(cv2.waitKey(1) == ord("q")):
                break
            # free camera object and exit
            
    cap.release()
    cv2.destroyAllWindows()


def video_stream():
    while True:       
        if not ret:
            break;
        else:
            ret, buffer = cv2.imencode('.jpeg',img)
            img = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + img +b'\r\n')
           

def streamINT():  
    @app.route('/camera')
    def camera():
        return render_template('camera.html')



    @app.route('/video')
    def video():
        return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host='127.0.0.1', port='5000', debug=False)
  

Thread(target = camerastream).start()
time.sleep(5)
Thread(target = streamINT).start()
