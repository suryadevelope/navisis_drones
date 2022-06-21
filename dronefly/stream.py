import cv2
import numpy as np
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
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("GMT: "+time.strftime("%a, %d %b %Y ", time.gmtime())+current_time+" GMT")
print(now.utcnow().strftime('%H:%M:%S'))
cap = cv2.VideoCapture(0)

# QR code detection object
#detector = cv2.QRCodeDetector()
app = Flask('__name__')

streamexternaldata = {"cloudqrid":"null"}

def streamfetchdata(condition,val):
    streamexternaldata[condition]=val


def startStream():
    Thread(target = camerastream).start()
    key_id = "2FLAAMMMAV7RZNCTGRH2"
    key_secret_id = "ZIwewYGla/56L50N7ZppXGVIZ8TAImI7ucyZ/+Q0"
    body =  {"query":"#Proxy connections can be generated to individual services and the unique\n#address will be provided in the host and port fields.\n#\n#hostIP values could contain\n#\n#0.0.0.0 for fully public connections available to user\n#\n#255.255.255.255 to allow only the first accessing IP to \"Latch\" the connection.\n#Blocking all others\n#\n#A unique public IP address to only allow that IP to access the connection\n\nmutation GetConnection($serviceId: String!, $hostIP: String!) {\n\tconnect(serviceId: $serviceId, hostIP: $hostIP) {\n\t\tid\n\t\tcreated\n\t\thost\n\t\tport\n\t\treverseProxy\n\t\ttimeout\n\t}\n}\n","variables":{"serviceId":"80:00:00:00:01:1C:06:C2","hostIP":"0.0.0.0"},"operationName":"GetConnection"}

    host = 'api.remote.it'
    url_path = '/graphql/v1'
    content_type_header = 'application/json'
    content_length_header = str(len(body))

    headers = {
        'host': host,
        'path': url_path,
        'content-type': content_type_header,
        'content-length': content_length_header,
    }

    response = requests.post('https://' + host + url_path,
                            json=body,
                            auth=HTTPSignatureAuth(algorithm="hmac-sha256",
                                                    key=b64decode(key_secret_id),
                                                    key_id=key_id,
                                                    headers=[
                                                        '(request-target)', 'host',
                                                        'date', 'content-type',
                                                        'content-length'
                                                    ]),
                            headers=headers)

    if response.status_code == 200:
        print(json.loads(response.text)["data"]["connect"]["host"]+":"+str(json.loads(response.text)["data"]["connect"]["port"])+"/video")
        return json.loads(response.text)["data"]["connect"]["host"]+":"+str(json.loads(response.text)["data"]["connect"]["port"])+"/video"
    
    else:
        print(response.status_code)
        return ""
    return ""
    

streamdata={"ret":"null","img":"null"}
def camerastream():

    while True:
        # get bounding box coords and data
        ret,img = cap.read()
        streamdata["ret"] = ret
        streamdata["img"] = img
        if not ret:
            break;
        elif np.sum(img) == 0:
            break;
        else:        
            #data, bbox, _ = detector.detectAndDecode(img)
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

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.get('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


def streamcamera():
    while True:
        if not streamdata["ret"]:
            break;
        else:
            ret, buffer = cv2.imencode('.jpeg',streamdata["img"])
            img = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + img +b'\r\n')

def streamINT():  
    @app.route('/camera')
    def camera():
        return render_template('camera.html')



    @app.route('/video')
    def video():
        return Response(streamcamera(), mimetype='multipart/x-mixed-replace; boundary=frame')

    app.run(host='127.0.0.1', port='5000', debug=False)
  


time.sleep(5)
Thread(target = streamINT).start()

