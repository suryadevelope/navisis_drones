import cv2
import numpy
from flask import Flask, render_template, Response, stream_with_context, request

import requests
import json
from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode

url = "https://api.remot3.it/apv/v27/device/connect"

payload = {
  "deviceaddress":"80:00:00:00:01:1C:06:BE",
  "wait": "true",
  "hostip": "0.0.0.0"
}



video = cv2.VideoCapture(0)
app = Flask('__name__')

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





import os
import requests
import json
from requests_http_signature import HTTPSignatureAuth
from base64 import b64decode
key_id = os.environ.get('R3_ACCESS_KEY_ID')
key_secret_id = os.environ.get('R3_SECRET_ACCESS_KEY')
body = {"query": "query { login { id email devices { items { id name }}}}"}
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
    print(response.text)
else:
    print(response.status_code)