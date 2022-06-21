import cv2
import numpy
from flask import Flask, render_template, Response, stream_with_context, request
from threading import Thread
import requests
import json
from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode
from datetime import datetime
import time

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("GMT: "+time.strftime("%a, %d %b %Y ", time.gmtime())+current_time+" GMT")

connectionid = "null"
video = cv2.VideoCapture(0)
app = Flask('__name__')

def start():
    def video_stream():
        while True:
            ret, frame = video.read()
            if not ret:
                break;
            else:
                ret, buffer = cv2.imencode('.jpeg',frame)
                frame = buffer.tobytes()
                yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')
        


    @app.route('/camera')
    def camera():
        return render_template('camera.html')



    @app.route('/video')
    def video_feed():
        
        return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


    app.run(host='127.0.0.1', port='5000', debug=False)

Thread(target = start).start()

time.sleep(10)


key_id = "ECKVSUSUQHAN6DEHGZ25"
key_secret_id = "XtwS5v/qR++1CtEUTDIZxAJj3pv/KIP64598O5La"
body =  {"query":"#Proxy connections can be generated to individual services and the unique\n#address will be provided in the host and port fields.\n#\n#hostIP values could contain\n#\n#0.0.0.0 for fully public connections available to user\n#\n#255.255.255.255 to allow only the first accessing IP to \"Latch\" the connection.\n#Blocking all others\n#\n#A unique public IP address to only allow that IP to access the connection\n\nmutation GetConnection($serviceId: String!, $hostIP: String!) {\n\tconnect(serviceId: $serviceId, hostIP: $hostIP) {\n\t\tid\n\t\tcreated\n\t\thost\n\t\tport\n\t\treverseProxy\n\t\ttimeout\n\t}\n}\n","variables":{"serviceId":"80:00:01:7F:7E:00:E7:47","hostIP":"0.0.0.0"},"operationName":"GetConnection"}

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
   
else:
    print(response.status_code)
  