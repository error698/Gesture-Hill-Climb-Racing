# Gesture-Controlled Hill Climb Racing

This project enables you to play Hill Climb Racing using hand gestures via a webcam. It uses MediaPipe for hand tracking and OpenCV for video processing, along with ctypes to simulate keypresses for controlling the game.

Features

Real-time hand tracking using the webcam

Control car movement with gestures:

Raise your palm → Accelerate

Close your fist → Brake

Works with Windows (uses ctypes for keypress simulation)

How It Works

Captures video using OpenCV

Tracks hand landmarks with MediaPipe

Detects gestures (open palm vs. closed fist)

Simulates keypresses (Right Arrow for acceleration, Left Arrow for braking)

Libraries Used

1. OpenCV (cv2)

Used for video capture and displaying frames

Converts frames from BGR to RGB (required for MediaPipe processing)

2. MediaPipe (mediapipe)

Provides hand tracking using MediaPipe Hands module

Detects finger landmarks to determine gestures

3. ctypes

Used to simulate keypresses for controlling the game

Sends virtual key events (Right Arrow, Left Arrow) to the system

Installation

Make sure you have Python installed, then run:

pip install opencv-python mediapipe

Running the Project

Run the script in the terminal:

python gesturecontrolhcr.py

Make sure your webcam is enabled and Hill Climb Racing is open!

Troubleshooting

"ModuleNotFoundError: No module named 'mediapipe'" → Run pip install mediapipe

"Error: Could not open webcam" → Check if another program is using the webcam

Gestures not recognized? → Ensure good lighting and clear background
