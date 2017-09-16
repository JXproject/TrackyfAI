import numpy as np
import cv2

cap = cv2.VideoCapture('VIRAT_S_000002.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_im = cv2.resize(gray, (960, 540))
    cv2.imshow('frame',resized_im)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
