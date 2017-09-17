import numpy as np
import cv2

cap = cv2.VideoCapture ('VIRAT_S_000200_01_000226_000268.mp4')
bgSub = cv2.createBackgroundSubtractorMOG2()

# class Blob:
#     centroidX = 0.0
#     centroidY = 0.0
#     area = 0.0
#     weight = 1.0
#     frames_alive = 0.0

#     def __init__(self, cX, cY, a, w, t):
#         self.centroidX = cX
#         self.centroidY = cY
#         self.area = a
#         self.weight = w
#         self.frames_alive = t

    #def calcCentroid()
        #return (,)

########BLOB#######
#params = cv2.SimpleBlobDetector_Params()

# Change thresholds
'''
params.minThreshold = 0
params.maxThreshold = 255

# Filter by Area.
params.filterByArea = True
params.minArea = 50

blobDet = cv2.SimpleBlobDetector_create(params)
'''
########BLOB#######

while True:
    ret, frame = cap.read()

    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgMask = bgSub.apply(grayFrame)

    ret, thresh = cv2.threshold(fgMask, 127, 255, cv2.THRESH_BINARY)

    #Morph Ops
    kernelE = np.ones((3,3), np.uint8)
    kernelD = np.ones((8, 8), np.uint8)
    thresh = cv2.erode(thresh, kernelE, iterations=1)
    thresh = cv2.dilate (thresh, kernelD, iterations = 1)
    thresh = cv2.dilate (thresh, kernelD, iterations = 1)
    thresh = cv2.dilate (thresh, kernelD, iterations = 1)
    thresh = cv2.dilate (thresh, kernelD, iterations = 1)
    cv2.imshow('thresh',thresh)

    #Bounding Box
    img2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    current_blobs = []
    for cnt in contours:
        M = cv2.moments(cnt)
        centroidX = int (M['m10']/M['m00'])
        centroidY = int (M['m01']/M['m00'])
        area = cv2.contourArea(cnt)

        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        frame = cv2.drawContours(frame, [box], 0, (0,255,0), 3)
        cv2.circle(frame, (centroidX, centroidY), 2, (0,255,0), -1)

        current_blobs.append({'cX':centroidX, 'cY':centroidY, 'area':area})

    #cv2.drawContours(frame, contours, -1, (0,0,255),1)
    cv2.imshow('frame', frame)

    #thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    #keyPoints = blobDet.detect(thresh)

    #imWKeypoints = cv2.drawKeypoints(frame, keyPoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    #cv2.imshow('KP', imWKeypoints)
    cv2.waitKey(20)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()