import time
from pyfirmata import Arduino, util
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from vidgear.gears import CamGear
from tracker import Tracker
import cvzone

# Define the pin numbers for the LEDs
led_pins = [8, 10, 12]

# Initialize YOLO model
model = YOLO('yolov8s.pt')

# Initialize camera stream
stream = CamGear(source='https://youtu.be/ii9JhNFy-8Q', stream_mode=True, logging=True).start() # YouTube Video URL as input


def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
# Initialize Arduino board
board = Arduino("COM3")  # Change 'COM3' to the correct port where your Arduino is connected



my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")
#print(class_list)
count=0
# Define the region of interest
area1 = [(490, 485), (512, 132), (677, 125), (957, 450)]

# Initialize the vehicle tracker
tracker = Tracker()

# Initialize the counters for each area
carcounter1 = []

while True:
    frame = stream.read()
    if frame is None:
        break

    # Resize frame
    frame = cv2.resize(frame, (1020, 500))

    # Detect objects using YOLO
    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    list = []
    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        if 'car' in c or 'motorcycle' in c or 'truck' in c or 'bus' in c:
            list.append([x1, y1, x2, y2])

    # Update tracker
    bbox_idx = tracker.update(list)
    for bbox in bbox_idx:
        x3, y3, x4, y4, id1 = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        result = cv2.pointPolygonTest(np.array(area1, np.int32), ((cx, cy)), False)
        if result >= 0:
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 255, 255), 2)
            cvzone.putTextRect(frame, f'{id1}', (x3, y3), 1, 1)
            if carcounter1.count(id1) == 0:
                carcounter1.append(id1)

    # Display area1
    cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 255, 0), 2)
    print(len(carcounter1))
    
    # Change green lighting time based on the number of detected vehicles
    if len(carcounter1) >= 5:
        green=15
    else:
        green=2
        
        
        
        
        
        board.digital[8].write(1)
        time.sleep(green)
        board.digital[8].write(0)
   
        board.digital[10].write(1)
        time.sleep(3)
        board.digital[10].write(0)
   
        board.digital[12].write(1)
        time.sleep(3)
        board.digital[12].write(0)

    # Display the frame
    cv2.imshow("RGB", frame)

    # Exit on ESC key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources
stream.stop()
board.exit()
cv2.destroyAllWindows()