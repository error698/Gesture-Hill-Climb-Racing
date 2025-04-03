# Gesture-Controlled Hill Climb Racing

This project enables you to play **Hill Climb Racing** using **hand gestures** via a webcam. It uses **MediaPipe** for hand tracking and **OpenCV** for video processing, along with **ctypes** to simulate keypresses for controlling the game.

## Features
- **Real-time hand tracking** using the webcam
- **Control car movement with gestures**:
  - **Raise your palm** → Accelerate
  - **Close your fist** → Brake
- **Works with Windows** (uses `ctypes` for keypress simulation)

## How It Works
1. **Captures video** using OpenCV
2. **Tracks hand landmarks** with MediaPipe
3. **Detects gestures** (open palm vs. closed fist)
4. **Simulates keypresses** (`Right Arrow` for acceleration, `Left Arrow` for braking)

## Libraries Used
### 1. **OpenCV** (`cv2`)
- Used for **video capture** and **displaying frames**
- Converts frames from **BGR to RGB** (required for MediaPipe processing)

### 2. **MediaPipe** (`mediapipe`)
- Provides **hand tracking** using **MediaPipe Hands** module
- Detects **finger landmarks** to determine gestures

### 3. **ctypes**
- Used to **simulate keypresses** for controlling the game
- Sends **virtual key events** (`Right Arrow`, `Left Arrow`) to the system

## Installation
Make sure you have Python installed, then run:
```sh
pip install opencv-python mediapipe
