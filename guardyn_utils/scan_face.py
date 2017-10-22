import numpy as np
import cv2
from os import getcwd
from colorthief import ColorThief
from math import sqrt, pow

face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('cascades/haarcascade_eye.xml')


def scan_face(img):
    valid = False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            valid = True
            factor = 0.2
            face = img[y:y+h, x:x+w]
            face_zoomed = img[int(y + h*factor):y+h - int(h*factor), x + int(factor*w):x+w - int(w*factor)]
    if valid:
        cv2.imwrite("images/" + "face_zoomed.png", face_zoomed)
        cv2.imwrite("images/" + "face.png", face)
        face_theif = ColorThief("images/face_zoomed.png")
        tone = _identify_skin_tone(face_theif.get_color(quality=1))
        # cv2.imshow("face", face)
        return tone

def _identify_skin_tone(tone):
    tone_labels = ['light', 'medium', 'dark']
    tone_clusters = [(120, 113, 115), (100, 92, 90), (78, 76, 88)]
    distances = []
    for i in range(0, len(tone_labels)):
        distances.append(pow(sqrt(pow(tone[0] - tone_clusters[i][0],2) + pow(tone[1] - tone_clusters[i][1],2) + pow(tone[2] - tone_clusters[i][2],2)),2))
    lowest = 0
    for i in range(0, len(distances)):
        if distances[i] < distances[lowest]:
            lowest = i
    return tone_labels[lowest]


