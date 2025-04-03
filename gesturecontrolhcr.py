import cv2
import numpy as np
from pynput.keyboard import Key, Controller
import time

# Initialize keyboard controller
keyboard = Controller()

def detect_hand(frame):
    """
    Detect hand in the frame using color-based segmentation
    Returns the hand contour and a binary mask
    """
    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define range for skin color detection (adjust these values based on your skin tone)
    # These values work for a range of skin tones but may need adjustment
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    
    # Create a binary mask for skin color
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # If no contours found, return None
    if not contours:
        return None, mask
    
    # Find the largest contour (assumed to be the hand)
    hand_contour = max(contours, key=cv2.contourArea)
    
    # Filter out small contours that are likely not hands
    if cv2.contourArea(hand_contour) < 5000:  # Minimum area threshold
        return None, mask
    
    return hand_contour, mask

def count_fingers(hand_contour, frame):
    """
    Count the number of extended fingers using convex hull and convexity defects
    Returns the number of fingers and a state (OPEN or CLOSED)
    """
    if hand_contour is None:
        return 0, "UNKNOWN"
    
    # Find the convex hull of the hand contour
    hull = cv2.convexHull(hand_contour, returnPoints=False)
    
    # Find convexity defects
    try:
        defects = cv2.convexityDefects(hand_contour, hull)
    except:
        # If convexity defects can't be calculated, return 0 fingers
        return 0, "UNKNOWN"
    
    if defects is None:
        return 0, "CLOSED"
    
    # Count fingers based on convexity defects
    finger_count = 0
    
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(hand_contour[s][0])
        end = tuple(hand_contour[e][0])
        far = tuple(hand_contour[f][0])
        
        # Calculate the triangle sides
        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        
        # Calculate the angle using cosine law
        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        
        # If angle is less than 90 degrees, it's likely a finger
        if angle <= np.pi / 2:  # 90 degrees in radians
            finger_count += 1
            # Draw a circle at the defect point
            cv2.circle(frame, far, 5, [0, 0, 255], -1)
    
    # Add 1 to finger count (for the thumb or another finger that might not create a defect)
    finger_count = min(finger_count + 1, 5)
    
    # Determine hand state based on finger count
    # More than 2 fingers extended is considered an open palm
    hand_state = "OPEN" if finger_count > 2 else "CLOSED"
    
    return finger_count, hand_state

def control_game(hand_state, prev_state):
    """
    Control the game based on hand state
    Open palm = gas (up arrow key)
    Closed palm = brake (down arrow key)
    """
    # Only send key commands when state changes to avoid flooding
    if hand_state != prev_state:
        # Release all keys first
        keyboard.release(Key.up)
        keyboard.release(Key.down)
        
        # Press the appropriate key based on hand state
        if hand_state == "OPEN":
            print("Action: GAS (Open Palm)")
            keyboard.press(Key.up)
        elif hand_state == "CLOSED":
            print("Action: BRAKE (Closed Palm)")
            keyboard.press(Key.down)
    
    return hand_state

def gesture_control():
    """
    Open camera, detect hand gestures, and control the game.
    Press 'q' to exit.
    """
    print("Starting gesture control for Hill Climb Racing...")
    print("Show OPEN PALM for GAS, CLOSED PALM for BRAKE")
    print("Press 'q' to exit")
    
    # Open webcam (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Create a background subtractor for better hand isolation
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
    
    # Variables to track state
    prev_hand_state = None
    
    # Main loop to capture and process frames
    while cap.isOpened():
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Flip horizontally for a more natural view (mirror-like)
        frame = cv2.flip(frame, 1)
        
        # Create a copy of the frame for display
        display_frame = frame.copy()
        
        # Apply background subtraction (optional, can help with hand isolation)
        # fg_mask = bg_subtractor.apply(frame)
        
        # Detect hand in the frame
        hand_contour, skin_mask = detect_hand(frame)
        
        # If a hand is detected
        if hand_contour is not None:
            # Draw the hand contour
            cv2.drawContours(display_frame, [hand_contour], 0, (0, 255, 0), 2)
            
            # Count fingers and determine hand state
            finger_count, hand_state = count_fingers(hand_contour, display_frame)
            
            # Control the game based on hand state
            if hand_state != "UNKNOWN":
                prev_hand_state = control_game(hand_state, prev_hand_state)
            
            # Display hand state and finger count on the frame
            cv2.putText(display_frame, f"Hand: {hand_state}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Fingers: {finger_count}", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display action on the frame
            if hand_state != "UNKNOWN":
                action = "GAS" if hand_state == "OPEN" else "BRAKE"
                cv2.putText(display_frame, f"Action: {action}", (10, 110), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            # If no hands detected, release all keys
            keyboard.release(Key.up)
            keyboard.release(Key.down)
            prev_hand_state = None
            
            # Display "No hands detected" on the frame
            cv2.putText(display_frame, "No hands detected", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Show the skin mask in a smaller window
        skin_mask_small = cv2.resize(skin_mask, (320, 240))
        cv2.imshow("Skin Mask", skin_mask_small)
        
        # Display the main frame
        cv2.imshow("Hill Climb Racing Gesture Control", display_frame)
        
        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release all keys before exiting
    keyboard.release(Key.up)
    keyboard.release(Key.down)
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Gesture control stopped.")

# Run the gesture control function if this script is executed directly
if __name__ == "__main__":
    # Give the user a moment to switch to the game window after starting the script
    print("Starting in 3 seconds... Switch to Hill Climb Racing game window!")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    gesture_control()
