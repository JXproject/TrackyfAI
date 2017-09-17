import cv2
import numpy as np
from functools import partial;
from functools import reduce;

def nothing(x):
    pass

def addToPath(blobsInFrame):
    if len(ObjsOfInterests) == 0:
        for currBlob in blobsInFrame:
            ObjsOfInterests.append({
                'coords': [(currBlob['cX'], currBlob['cY'])],
                'elapsedFrames': 1,
                #'weight': currBlob['weight']
            });
    else:
        prevCoords = reduce((lambda x, y: x['coords'][-1]), ObjsOfInterests);
        for currBlob in blobsInFrame:
            currBlobCoord = (currBlob['cX'], currBlob['cY'])
            nearestPrevBlob = min(prevCoords, key=partial(calcDist, currBlobCoord))
            if calcDist(currBlobCoord, nearestPrevBlob) < DIST_THRESHOLD:
                blobIndex = [y for y in prevCoords].index(nearestPrevBlob);
                ObjsOfInterests[blobIndex]['coords'][-1].append(currBlobCoord);
                #ObjsOfInterests[blobIndex]['elapsedFrames']+=1;
                #ObjsOfInterests[blobIndex]['weight'] += currBlob['weight']
            else:
                ObjsOfInterests.append({
                    'coords': currBlobCoord,
                    'elapsedFrames': 1,
                    #'weight': blob['weight']
                })

def drawObjectPaths():
    print(ObjsOfInterests)
    



ObjsOfInterests = []
DIST_THRESHOLD = 0.01

calcDist = lambda s, d: (s[0]-d[0])**2+(s[1]-d[1])**2

# Create a black image, a window

#img = np.zeros((20,20,3), np.uint8)
cv2.namedWindow('image')
#videoFrame = np.zeros((500,890,3), np.uint8)

# create trackbars for color change
cv2.createTrackbar('Moving Objects','image',0,100,nothing)
cv2.createTrackbar('Object Trajectory','image',0,100,nothing)
cv2.createTrackbar('Heat Map','image',0,100,nothing)

# create switch for ON/OFF functionality
switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'image',0,1,nothing)

cap = cv2.VideoCapture('VIRAT_S_000002.mp4')
bgSub = cv2.createBackgroundSubtractorMOG2()

while(1):
    ret, videoFrame = cap.read()
    videoFrame = cv2.resize(videoFrame, (960, 540))

    grayFrame = cv2.cvtColor(videoFrame, cv2.COLOR_BGR2GRAY)
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
        videoFrame = cv2.drawContours(videoFrame, [box], 0, (0,255,0), 3)
        cv2.circle(videoFrame, (centroidX, centroidY), 2, (0,255,0), -1)

        current_blobs.append({'cX':centroidX, 'cY':centroidY, 'area':area})

    addToPath(current_blobs)
    drawObjectPaths()

    #Draw lines




    #cv2.drawContours(frame, contours, -1, (0,0,255),1)
    #cv2.imshow('frame', videoFrame)

    # get current positions of four trackbars
    r = cv2.getTrackbarPos('Moving Objects','image')
    g = cv2.getTrackbarPos('Object Trajectory','image')
    b = cv2.getTrackbarPos('Heat Map','image')
    s = cv2.getTrackbarPos(switch,'image')


    if s == 0:
        videoFrame = cv2.rectangle(videoFrame, (0, 0), (960, 540), (r,g,b), 5)
    else:
        videoFrame = cv2.rectangle(videoFrame, (0, 0), (960, 540), (r,g,b), -1)
    

    #print(r/100)
    #cv2.addWeighted(mergeRectangle, r/100, videoFrame, 1 - r/100, 0, videoFrame)

    cv2.imshow('image',videoFrame)
    k = cv2.waitKey(25) & 0xFF
    if k == 27: #esc is pressed
        break



cv2.destroyAllWindows()