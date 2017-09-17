import numpy as np
import cv2
import random
import math
import colorsys

# ==================================FUNCTIONS================================
#Heat Map Color  0 blue <-> 1 red
def HeatMapClr(weight_):
    return colorsys.hsv_to_rgb((weight_)*2.0/3.0, math.sqrt(weight_), 1)

#HeatMapAssign
def Heat_Map_Generate(DataMat_, width_, height_):
   Amount_x = len(DataMat_[0])
   Amount_y = len(DataMat_)
   HeatMap_img = np.zeros((Amount_y, Amount_x, 3), dtype=np.uint8)
   xPos, yPos = 0, 0
   while xPos < Amount_x : #Loop through rows
       while yPos < Amount_y : #Loop through collumns
           HeatMap_Clr = HeatMapClr(DataMat_[yPos][xPos])
           HeatMap_img.itemset((yPos, xPos, 0), HeatMap_Clr[0]*255) #Set B to 255
           HeatMap_img.itemset((yPos, xPos, 1), HeatMap_Clr[1]*255) #Set G to 255
           HeatMap_img.itemset((yPos, xPos, 2), HeatMap_Clr[2]*255) #Set R to 255
           yPos = yPos + 1 #Increment Y position by 1

       yPos = 0
       xPos = xPos + 1 #Increment X position by 1
   return cv2.resize(HeatMap_img, (int(width_), int(height_)));

# Update Heap Mat Accumulate Data
def Heat_Map_Data_Mat_Update (DataMat_, x_, y_, Screen_Width_, Screen_Height_, weight):
    if(x_<=Scene_Width and y_<=Scene_Height and x_>=0 and y_>=0):
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
                    Prev_Value = CentreValue + weight*factor
                    if (Prev_Value > 1):
                        DataMat_[index_y][index_x] = 1
                    elif (Prev_Value < 0):
                        DataMat_[index_y][index_x] = 0
                    else :
                        DataMat_[index_y][index_x] = Prev_Value
        #CODE
    return DataMat_
# ==================================INITIALIZATION================================
#Predefine Video Source
cap = cv2.VideoCapture('VIRAT_S_000002.mp4')
#Frame Counter
Frame_Counter = 0
#Font Style for OnGUI info
font = cv2.FONT_HERSHEY_SIMPLEX
#Screen height and width
Scene_Height = -1.0
Scene_Width = -1.0

#Backgroud Subtractor define
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# fgbg = cv2.createBackgroundSubtractorMOG2()

# Accumulative Heat Mat Data 0-1 | [0]x-resolution [1]y-resolution
Accumulative_Heat_Mat = np.zeros((5,5))

# ==================================BODY================================
while(cap.isOpened()):
    # Read One Frame
    ret, frame = cap.read()

    # Update Scene Size
    if (Scene_Width==-1.0 or Scene_Height==-1.0):
        Scene_Height, Scene_Width, Channel = frame.shape
        Scene_Height/=2;
        Scene_Width/=2;
    # Resize Scene
    cap_resized = cv2.resize(frame, (int(Scene_Width), int(Scene_Height)))
    cap_resized_gray = cv2.cvtColor(cap_resized, cv2.COLOR_BGR2GRAY) #Gray Scale

    # Backgroud Subtractor
    # cap_resized_gray_bgSub = fgbg.apply(frame)
    # cap_resized_gray_bgSub = cv2.morphologyEx(cap_gray_bgSub, cv2.MORPH_OPEN, kernel)

    # Heat Map
    Accumulative_Heat_Mat = Heat_Map_Data_Mat_Update(Accumulative_Heat_Mat, Scene_Width*random.uniform(0,1) ,Scene_Height*random.uniform(0,1), Scene_Width ,Scene_Height ,0.1);
    HeatMap_img_resized = Heat_Map_Generate(Accumulative_Heat_Mat, Scene_Width, Scene_Height)

    # Backgroud Subtractor
    # ret,thresh = cv2.threshold(cap_gray_bgSub_resized,127,255,0)
    # image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #image = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    # image = cv2.drawContours(image, contours, -1, (0,255,0), 3)
    #cap_gray_bgSub_resized_clred = cv2.cvtColor(cap_gray_bgSub_resized,cv2.COLOR_GRAY2BGR)

    # On GUI Display
    cv2.putText(cap_resized,'Frame @ {}'.format(Frame_Counter),(10,25), font, 1, (255,255,255), 2)

    # Scene Blending
    Result_Scene = cv2.addWeighted(cap_resized,1,HeatMap_img_resized,1,0)
    # Result_Scene = HeatMap_img_resized
    cv2.imshow('frame',Result_Scene)

    # Frame Incrementing
    Frame_Counter+=1

    # Key Handling
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==================================END================================
cap.release()
cv2.destroyAllWindows()
