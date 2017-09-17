import cv2
import numpy as np
from functools import partial
from functools import reduce
import random
import math
import colorsys

ObjsOfInterests = []
DIST_THRESHOLD = 0.2
#Font Style for OnGUI info
font = cv2.FONT_HERSHEY_SIMPLEX
#Screen height and width
Scene_Height = -1.0
Scene_Width = -1.0

Global_Full_Heat_Area_Counter = 0
CONST_MAX_HEAT_AREA_TOLERANCE = 0.4
CONST_HEAT_MAP_RESOLUTION = 10

# ==================================FUNCTIONS================================
#Heat Map Color  0 blue <-> 1 red  math.sqrt(weight_)
def HeatMapClr(weight_):
    S_value = 1
    if(weight_==0):
        S_value = 0
    return colorsys.hsv_to_rgb((weight_)*2.0/3.0, S_value, 1)

#Calculate distance between a blob in the current frame, and all the blobs in the previous frame
def calcDist(prevCoords, currBlobCoord):
    euclidDist = [];
    for coord in prevCoords:
        #print('value of coord[0]: ', coord)
        euclidDist.append((coord[0]-currBlobCoord[0])**2 +(coord[1]-currBlobCoord[1])**2)
    return euclidDist;
#
#HeatMapAssign
def Heat_Map_Generate(DataMat_, width_, height_):
   Amount_x = len(DataMat_[0])
   Amount_y = len(DataMat_)
   HeatMap_img = np.zeros((Amount_y, Amount_x, 3), dtype=np.uint8)
   xPos, yPos = 0, 0
   while xPos < Amount_x : #Loop through rows
       while yPos < Amount_y : #Loop through collumns
           HeatMap_Clr = HeatMapClr(DataMat_[yPos][xPos])
           ##print(DataMat_)
           HeatMap_img.itemset((yPos, xPos, 0), HeatMap_Clr[0]*255) #Set B to 255
           HeatMap_img.itemset((yPos, xPos, 1), HeatMap_Clr[1]*255) #Set G to 255
           HeatMap_img.itemset((yPos, xPos, 2), HeatMap_Clr[2]*255) #Set R to 255
           yPos = yPos + 1 #Increment Y position by 1

       yPos = 0
       xPos = xPos + 1 #Increment X position by 1
   return cv2.resize(HeatMap_img, (int(width_), int(height_)));

# Update Heap Mat Accumulate Data
def Heat_Map_Data_Mat_Update (DataMat_, x_, y_, Screen_Width_, Screen_Height_, weight_, Global_Full_Heat_Area_Counter_):

    if(x_<=Screen_Width_ and y_<=Screen_Height_ and x_>=0 and y_>=0):
        Unit_x = Screen_Width_/(len(DataMat_[0])-1)
        Unit_y = Screen_Height_/(len(DataMat_)-1)
        index_x_Centre = round(x_/Unit_x)
        index_y_Centre = round(y_/Unit_y)
        CentreValue = DataMat_[index_y_Centre][index_x_Centre]
        #Will bring Up surrounding values
        for i in range(0,1):
            index_x = index_x_Centre + i
            for j in range(0,1):
                index_y = index_y_Centre + j
                factor = 1 - (abs(i)+abs(j))/3 #Distance Factor
                if (index_y<len(DataMat_) and index_x<len(DataMat_[0]) and index_x>=0 and index_y>=0) :
                    Prev_Value = CentreValue + weight_*factor
                    if (Prev_Value >= 1):
                        if (DataMat_[index_y][index_x] != 1):
                            Global_Full_Heat_Area_Counter_ += 1;
                        DataMat_[index_y][index_x] = 1
                    elif (Prev_Value < 0):
                        DataMat_[index_y][index_x] = 0
                    else :
                        DataMat_[index_y][index_x] = Prev_Value
        #CODE

    return (DataMat_,Global_Full_Heat_Area_Counter_)

def Heat_Map_Dissipate (DataMat_, dispateWeight, Reset):
    if (Reset):
        dispateWeight = 0
    for i in range(0,len(DataMat_)):
        for j in range(0,len(DataMat_[0])):
            DataMat_[j][i] *= dispateWeight

    return DataMat_


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
        prevCoords = [];
        for blob in ObjsOfInterests:
            prevCoords.append(blob['coords'][-1]);
        #print('ObjsOfInterests', ObjsOfInterests)
        #print('prevCoords',prevCoords)
        for currBlob in blobsInFrame:
            currBlobCoord = (currBlob['cX'], currBlob['cY'])
            distToBlobs = calcDist(prevCoords, currBlobCoord);
            minDist = min(distToBlobs);
            blobIndex = distToBlobs.index(minDist);
            nearestPrevBlob = prevCoords[blobIndex];

            if minDist < DIST_THRESHOLD:
                ObjsOfInterests[blobIndex]['coords'].append(currBlobCoord);
                ObjsOfInterests[blobIndex]['elapsedFrames']+=1;
                #ObjsOfInterests[blobIndex]['weight'] += currBlob['weight']
            else:
                ObjsOfInterests.append({
                    'coords': [currBlobCoord],
                    'elapsedFrames': 1
                    #'weight': blob['weight']
                })

def drawObjectPaths(videoFrame):
    #print(ObjsOfInterests)
    for blob in ObjsOfInterests:
        blobCoordHist = blob['coords'];
        if len(blobCoordHist) > 2:
            cv2.arrowedLine(videoFrame, blobCoordHist[-2], blobCoordHist[-1], (0,0,255), 5,8,0,0.1);


    #======================================================== END OF FUNCTIONS ===============================#


#======INITIALIZATION=============



# Create a black image, a window

#img = np.zeros((20,20,3), np.uint8)
cv2.namedWindow('image')
#videoFrame = np.zeros((500,890,3), np.uint8)

# create trackbars for color change
cv2.createTrackbar('Moving Objects','image',0,1,nothing)
cv2.createTrackbar('Object Trajectory','image',0,1,nothing)
cv2.createTrackbar('Heat Map','image',0,100,nothing)

# create switch for ON/OFF functionality
switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'image',0,1,nothing)

cap = cv2.VideoCapture('VIRAT_S_000002.mp4')
bgSub = cv2.createBackgroundSubtractorMOG2()

#Frame Counter
Frame_Counter = 0
#Font Style for OnGUI info
font = cv2.FONT_HERSHEY_SIMPLEX
#Screen height and width
Scene_Height = -1.0
Scene_Width = -1.0

Accumulative_Heat_Mat = np.zeros((CONST_HEAT_MAP_RESOLUTION,CONST_HEAT_MAP_RESOLUTION))


#========START OF APPLICATION=========#

while(1):
    Frame_Counter += 1
    ret, videoFrame = cap.read()
    videoFrame = cv2.resize(videoFrame, (960, 540))

    # get current positions of four trackbars
    r = cv2.getTrackbarPos('Moving Objects','image')
    g = cv2.getTrackbarPos('Object Trajectory','image')
    b = cv2.getTrackbarPos('Heat Map','image')
    s = cv2.getTrackbarPos(switch,'image')

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
    #videoFrame = cv2.resize(videoFrame, (600,300))
    for cnt in contours:
        M = cv2.moments(cnt)
        centroidX = int (M['m10']/M['m00'])
        centroidY = int (M['m01']/M['m00'])
        area = cv2.contourArea(cnt)

        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        #toggle contours on and off
        videoFrame = cv2.drawContours(videoFrame, [box], 0, (0,255,0), 3)
        cv2.circle(videoFrame, (centroidX, centroidY), 2, (0,255,0), -1)

        current_blobs.append({'cX':centroidX, 'cY':centroidY, 'area':area})
        addToPath(current_blobs)

        if r == 1: #only triggers contour drawing if the GUI toggle is on
            drawObjectPaths(videoFrame)

    # Heat Map
    ratio = Global_Full_Heat_Area_Counter/(len(Accumulative_Heat_Mat)+len(Accumulative_Heat_Mat[0]))
    if(ratio > CONST_MAX_HEAT_AREA_TOLERANCE):
        Accumulative_Heat_Mat = Heat_Map_Dissipate (Accumulative_Heat_Mat, 0.95, False)
        ratio = 0
        Global_Full_Heat_Area_Counter = 0
    #10 frames
    if(Frame_Counter%10 == 0):
        # print(len(current_blobs))
        for index in range(0,len(current_blobs)):
            tempDataHandler = Heat_Map_Data_Mat_Update(Accumulative_Heat_Mat, current_blobs[index]['cX'], current_blobs[index]['cY'], 960 , 540 ,0.01, Global_Full_Heat_Area_Counter)
            Accumulative_Heat_Mat = tempDataHandler[0]
            Global_Full_Heat_Area_Counter = tempDataHandler[1]
    HeatMap_img_resized = Heat_Map_Generate(Accumulative_Heat_Mat, 960, 540)


    #Draw lines




    #cv2.drawContours(frame, contours, -1, (0,0,255),1)
    #cv2.imshow('frame', videoFrame)


    if s == 0:
        videoFrame = cv2.rectangle(videoFrame, (0, 0), (960, 540), (r,g,b), 5)
    else:
        videoFrame = cv2.rectangle(videoFrame, (0, 0), (960, 540), (r,g,b), -1)

    if r == 0:
        videoFrame = cv2.addWeighted(videoFrame, 1, HeatMap_img_resized, b/100.0, 0) #change to global variable
    else:
        videoFrame = cv2.addWeighted(videoFrame, 1, HeatMap_img_resized, b/100.0, 0) #change to global variable


    #print(r/100)
    #cv2.addWeighted(mergeRectangle, r/100, videoFrame, 1 - r/100, 0, videoFrame)

    cv2.imshow('image', videoFrame)
    k = cv2.waitKey(25) & 0xFF
    if k == 27: #esc is pressed
        break



cv2.destroyAllWindows()
