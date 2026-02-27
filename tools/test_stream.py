import cv2
import sys
import time

rtsp_url = "rtsp://admin:Sanlorenz0@192.168.1.56:554/Streaming/Channels/101"

print(f"Connecting to {rtsp_url}...")
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    sys.exit(1)

ret, frame = cap.read()
if ret:
    print(f"Success! Frame shape: {frame.shape}")
    print("Frame read successfully.")
else:
    print("Error: Could not read frame.")
    sys.exit(1)

cap.release()
