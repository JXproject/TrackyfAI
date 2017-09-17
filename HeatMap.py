import numpy as np
import cv2

# ==================================FUNCTIONS================================
#HeatMapAssign
def Heat_Map_Generate( DataMat_, width_, height_):
   HeatMap_img = np.zeros((len(HA[0]), len(HA), 3), dtype=np.uint8)
   xPos, yPos = 0, 0
   while xPos < len(DataMat_): #Loop through rows
       while yPos < len(DataMat_[0]): #Loop through collumns

           HeatMap_img.itemset((yPos, xPos, 0), 255-int(DataMat_[xPos][yPos]*255)) #Set B to 255
           HeatMap_img.itemset((yPos, xPos, 1), 255) #Set G to 255
           HeatMap_img.itemset((yPos, xPos, 2), 255) #Set R to 255
           yPos = yPos + 1 #Increment Y position by 1

       yPos = 0
       xPos = xPos + 1 #Increment X position by 1
   return cv2.resize(HeatMap_img, (int(width_), int(height_)));

# Update Heap Mat Accumulate Data
def Heat_Map_Data_Mat_Update (DataMat_, x_, y_, weight):
    if (y_<(len(HA[0])) and x_<(len(HA))) :
        Prev_Value = DataMat_[y_][x_]
        Prev_Value += weight
        if (Prev_Value > 1):
            DataMat_[y_][x_] = 1
        elif (Prev_Value < 0):
            DataMat_[y_][x_] = 0
        else :
            DataMat_[y_][x_] = Prev_Value
    #CODE
    return HeatMat_
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

# Accumulative Heap Mat Data 0-1
HA = np.array([[1, 0.762, 0.954, 0.000, 0.835, 1],
               [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
               [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
               [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
               [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
               [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
               [1, 0.682, 0.755, 0.708, 0.643, 1]])

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
    HeatMap_img_resized = Heat_Map_Generate(HA, Scene_Width, Scene_Height)

    # Backgroud Subtractor
    # ret,thresh = cv2.threshold(cap_gray_bgSub_resized,127,255,0)
    # image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #image = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    # image = cv2.drawContours(image, contours, -1, (0,255,0), 3)
    #cap_gray_bgSub_resized_clred = cv2.cvtColor(cap_gray_bgSub_resized,cv2.COLOR_GRAY2BGR)

    # On GUI Display
    cv2.putText(cap_resized,'Frame @ {}'.format(Frame_Counter),(10,25), font, 1, (255,255,255), 2)

    # Scene Blending
    Result_Scene = cv2.addWeighted(cap_resized,1,HeatMap_img_resized,0.3,0)
    cv2.imshow('frame',Result_Scene)

    # Frame Incrementing
    Frame_Counter+=1

    # Key Handling
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==================================END================================
cap.release()
cv2.destroyAllWindows()
