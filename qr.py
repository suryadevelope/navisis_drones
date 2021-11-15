import pyzbar.pyzbar as pyzbar
import cv2

cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()


while True:

    _, img = cap.read()
    
    decodedObjects = pyzbar.decode(img)
    for decodedObject in decodedObjects:
        points = decodedObject.polygon
        left = decodedObject.rect[0]
        top = decodedObject.rect[1]
        height = decodedObject.rect[3]
        width = decodedObject.rect[2]
        data = decodedObject.data
        
        print(data)
        print(data == b'surya')
        print("completed")
    cv2.imshow("code detector", img)
