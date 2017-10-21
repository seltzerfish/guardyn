from imutils.video import VideoStream
import numpy as np
import imutils
from time import sleep, time
import cv2
import png
import _thread
from copy import deepcopy
import os
from guardyn_utils import send_alerts

# CONSTANTS
cwd = str(os.getcwd())
COOLDOWN_SECONDS = 10
BLINK_DURATION = 14 # frames
CONFIDENCE = 0.5
WEAPON_CONFIDENCE = 0.85
PERSON_INDEX = 15
WEAPON_INDEX = 5
MAX_IMAGE_WIDTH = 420
MAX_DISPLAY_WIDTH = 850
CAFFEMODEL = cwd + "/models/" + "MobileNetSSD_deploy.caffemodel"
PROTOTXT = cwd + "/models/" + "MobileNetSSD_deploy.prototxt.txt"

CLASSES = ["background", "airplane", "bicycle", "bird", "boat",
    "weapon", "bus", "car", "cat", "chair", "cow", "dining_table",
    "dog", "horse", "motorbike", "human", "potted_plant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
COLORS[WEAPON_INDEX] = [0, 0, 255]
COLORS[PERSON_INDEX] = [0, 255, 0]

# VARIABLES
should_screenshot = False
blinking = False
cooldown = False
cooldown_benchmark = None
screenshot_frame = False
blink_count = 0

# SETUP
print("Loading Tensorflow Model...")
model = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
print("Starting VideoStream...")
videostream = VideoStream().start()
sleep(0.5)

# VIDEO LOOP
while True:
    frame = videostream.read()
    frame = imutils.resize(frame, width=MAX_DISPLAY_WIDTH)
    overlay = deepcopy(frame)
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
        0.007843, (300, 300), 127.5)
    if blinking:
        if blink_count > BLINK_DURATION:
            blinking = False
            blink_count = 0
        else:
            blink_count += 1
    if cooldown:
        if time() - cooldown_benchmark >= COOLDOWN_SECONDS:
            cooldown = False
            cooldown_benchmark = None
    model.setInput(blob)
    detections = model.forward()
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        index = int(detections[0, 0, i, 1])
        if (index == WEAPON_INDEX or index == PERSON_INDEX) and confidence > CONFIDENCE:

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            if index == WEAPON_INDEX and confidence >= WEAPON_CONFIDENCE and not cooldown:
                _thread.start_new_thread(send_alerts.text_alert, ("DANGEROUS WEAPON DETECTED NEARBY.",))
                cooldown_benchmark = time()
                blinking = True
                cooldown = True
                screenshot_frame = True
                should_screenshot = True


            label = "{}: {:.2f}%".format(CLASSES[index],
                confidence * 100)

            if blinking and index == WEAPON_INDEX and (blink_count + 1) % 2 == 0:
                cv2.rectangle(overlay, (startX, startY), (endX, endY),
                    COLORS[index], -1)
                cv2.addWeighted(overlay, 0.5, frame, 0.5,
                    0, frame)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255, 255, 255], 2)
            if screenshot_frame and index == PERSON_INDEX:
                screenshot_frame = False
            else:
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    COLORS[index], 2)
                if index == WEAPON_INDEX:
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255, 255, 255], 2)

    if should_screenshot:
        should_screenshot = False
        cv2.imwrite(cwd + "/images/" + "suspect.png", imutils.resize(frame, width=MAX_IMAGE_WIDTH))
        _thread.start_new_thread(send_alerts.image_alert, (cwd + "/images/" + "suspect.png",))
    if cooldown: 
        cv2.putText(frame, "THREAT DETECTED",
            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
videostream.stop()