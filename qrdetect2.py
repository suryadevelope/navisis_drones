
# Python code to find the co-ordinates of
# the contours detected in an image.
import numpy as np
import cv2

print("started")
cap = cv2.VideoCapture(0)


# QR code detection object
detector = cv2.QRCodeDetector()

while True:
    # get the image
    _, img = cap.read()
        # Reading image
    # font = cv2.FONT_HERSHEY_COMPLEX
    # # Converting image to a binary image
    # # ( black and white only image).
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, threshold = cv2.threshold(img_gray, 110, 255, cv2.THRESH_BINARY)

    # # Detecting contours in image.
    # contours, _ = cv2.findContours(threshold, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # # get bounding box coords and data
    # data, bbox, _ = detector.detectAndDecode(img)
   
    def show_image(image):
        cv2.imshow('image',image)
        c = cv2.waitKey()
        if c >= 0 : return -1
        return 0

    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, im = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY_INV)
    # contours, hierarchy  = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # img = cv2.drawContours(im, contours, -1, (0,255,75), 2)
    # show_image(img)
    
    # for cnt in contours:

    #     approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)

    #     # draws boundary of contours.
    #     cv2.drawContours(img, [approx], 0, (0, 0, 255), 5)

    #     # Used to flatted the array containing
    #     # the co-ordinates of the vertices.
    #     n = approx.ravel()
    #     i = 0

    #     for j in n:
    #         if(i % 2 == 0):
    #             x = n[i]
    #             y = n[i + 1]

    #             # String containing the co-ordinates.
    #             string = str(x) + " " + str(y)

    #             if(i == 0):
    #                 # text on topmost co-ordinate.
    #                 cv2.putText(img, "Arrow tip", (x, y),
    #                             font, 0.5, (255, 0, 0))
    #             else:
    #                 # text on remaining co-ordinates.
    #                 cv2.putText(img, string, (x, y),
    #                             font, 0.5, (0, 255, 0))
    #         i = i + 1

    #         # Showing the final image.
    #         cv2.imshow('image', img)

    #         # display size 
    #         if data == "surya":
    #             print(' width:', sum( mask.any(axis=0) ))
    #             print('height:', sum( mask.any(axis=1) ))

       
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break
# free camera object and exit
cap.release()
cv2.destroyAllWindows()


