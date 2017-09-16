import numpy as np
import cv2
#Predefine
cap = cv2.VideoCapture('VIRAT_S_000002.mp4')
counter = 0
font = cv2.FONT_HERSHEY_SIMPLEX

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
fgbg = cv2.createBackgroundSubtractorMOG2()
#Body
while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = fgbg.apply(frame)
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    
    resized_im = cv2.resize(gray, (960, 540))
    
    cv2.putText(resized_im,'Frame @ {}'.format(counter),(10,25), font, 1,(255,255,255),2)
    cv2.imshow('frame',resized_im)
    counter+=1
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(img,'OpenCV',(10,200), font, 4,(10,10,80),2,cv2.LINE_AA)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#END
cap.release()
cv2.destroyAllWindows()

