from imutils.video import VideoStream
import numpy as np
import imutils
from time import sleep
import cv2
import png
import os
from guardyn_utils import send_alerts

cwd = str(os.getcwd())

CONFIDENCE = 0.5
WEAPON_CONFIDENCE = 0.85
PERSON_INDEX = 15
WEAPON_INDEX = 5
MAX_IMAGE_WIDTH = 800
CAFFEMODEL = cwd + "/models/" + "MobileNetSSD_deploy.caffemodel"
PROTOTXT = cwd + "/models/" + "MobileNetSSD_deploy.prototxt.txt"

CLASSES = ["background", "airplane", "bicycle", "bird", "boat",
    "weapon", "bus", "car", "cat", "chair", "cow", "dining_table",
    "dog", "horse", "motorbike", "human", "potted_plant", "sheep",
    "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
COLORS[WEAPON_INDEX] = [0, 0, 255]
COLORS[PERSON_INDEX] = [0, 255, 0]


print("Loading Tensorflow Model...")
model = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
print("Starting VideoStream...")
videostream = VideoStream().start()
sleep(0.5)
should_screenshot = False
found = False
while True:
    frame = videostream.read()
    frame = imutils.resize(frame, width=MAX_IMAGE_WIDTH)

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
        0.007843, (300, 300), 127.5)

    model.setInput(blob)
    detections = model.forward()
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        index = int(detections[0, 0, i, 1])
        if (index == WEAPON_INDEX or index == PERSON_INDEX) and confidence > CONFIDENCE:

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            if index == WEAPON_INDEX and found == False and confidence >= WEAPON_CONFIDENCE:
                found = True
                should_screenshot = True
                send_alerts.text_alert("Dangerous weapon detected nearby")

            label = "{}: {:.2f}%".format(CLASSES[index],
                confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                COLORS[index], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255, 255, 255], 2)

    if should_screenshot:
        should_screenshot = False
        cv2.imwrite(cwd + "/images/" + "suspect.png", frame)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    # fps.update()

# stop the timer and display FPS information
# fps.stop()
# print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
videostream.stop()