import cv2
import time
import ctypes
import sys

try:
    import mediapipe as mp
except ModuleNotFoundError:
    print("Error: The 'mediapipe' module is not installed. Please install it using 'pip install mediapipe'.")
    sys.exit(1)

# Direct keys for simulating keypress
SendInput = ctypes.windll.user32.SendInput

# Key codes for arrow keys
LEFT_ARROW = 0x25
RIGHT_ARROW = 0x27

# Function to press a key
def press_key(hexKeyCode):
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0, 0)

# Function to release a key
def release_key(hexKeyCode):
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 2, 0)

# Initialize Mediapipe Hand Tracking with configurable confidence
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=DETECTION_CONFIDENCE, min_tracking_confidence=TRACKING_CONFIDENCE)
mp_draw = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame from webcam.")
        break
    
    frame = cv2.flip(frame, 1)  # Flip horizontally for natural interaction
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Extract landmark positions
            landmarks = hand_landmarks.landmark
            index_tip = landmarks[8].y  # Index finger tip
            wrist = landmarks[0].y      # Wrist position
            
            # Detect open hand (accelerate) vs closed fist (brake)
            if index_tip < wrist - 0.1:
                press_key(RIGHT_ARROW)
                release_key(LEFT_ARROW)
            elif index_tip > wrist - 0.05:
                press_key(LEFT_ARROW)
                release_key(RIGHT_ARROW)
            else:
                release_key(RIGHT_ARROW)
                release_key(LEFT_ARROW)
    
    # Show output frame
    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
