import cv2
import time
import RPi.GPIO as GPIO
import math
import os
import socket

# Server Configuration
HOST = "192.168.1.17"  # Enter IP or Hostname of your server
PORT = 8005  # Pick an open Port (1009+ recommended), must match the server port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Load class names
classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# Load model configuration
configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
red = 9
yellow = 10
green = 11
GPIO.setup(red, GPIO.OUT)
GPIO.setup(yellow, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    objectInfo = []
    
    if len(objects) == 0:
        objects = classNames
    
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append(["car"])
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, className.upper(), (box[0] + 10, box[1] + 30), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30), 
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    
    return img, objectInfo

if __name__ == "__main__":
    cycle = 5
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    cap.set(10, 50)
    
    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img, 0.30, 0.4, objects=['car'])
        print(objectInfo)
        cv2.imshow("Output", img)
        
        if objectInfo == [['car']]:
            R = 1 / 1
        elif objectInfo == [['car'], ['car']]:
            R = 2 / 1
        elif objectInfo == [['car'], ['car'], ['car']]:
            R = 3 / 1
        elif objectInfo == [['car'], ['car'], ['car'], ['car']]:
            R = 4 / 1
        else:
            g = cycle / 2
            r = cycle / 2
            continue
        
        Gama = (math.sqrt(R)) / (math.sqrt(R) + 1)
        g = Gama * cycle
        r = cycle - (Gama * cycle)
        
        GPIO.output(red, False)
        GPIO.output(yellow, False)
        GPIO.output(green, True)
        time.sleep(g)
        print(g, "seconds as green")
        
        GPIO.output(red, True)
        GPIO.output(yellow, False)
        GPIO.output(green, False)
        time.sleep(r)
        print(r, "seconds as red")
        
        command = "Traffic Update"
        s.send(str.encode(command))
        reply = s.recv(1024).decode('utf-8')
        if reply == 'Terminate':
            break
        print(reply)
    
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
