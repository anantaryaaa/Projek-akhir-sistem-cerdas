import cv2
import numpy as np
from handTrackingModule import handDetector

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    
    # Create canvas for drawing
    canvas = np.zeros((480, 640, 3), np.uint8)
    
    # Previous point coordinates
    px, py = 0, 0

    # Create fullscreen window
    window_name = "Drawing"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        # Get camera frame
        success, img = cap.read()
        img = cv2.flip(img, 1)  # Mirror image
        
        # Find hand landmarks
        img = detector.findHands(img)
        lm_list = detector.findPosition(img, draw=False)
        
        if len(lm_list) > 0:  # If hand detected
            # Get index finger tip coordinates
            x, y = lm_list[8][1], lm_list[8][2]
            
            # Draw line if not first point
            if px == 0 and py == 0:
                px, py = x, y
            else:
                # Draw on both canvas and image
                cv2.line(canvas, (px, py), (x, y), (0, 0, 255), 15)
                cv2.line(img, (px, py), (x, y), (0, 0, 255), 15)
            
            # Update previous point
            px, py = x, y
        else:
            # Reset previous point when hand not detected
            px, py = 0, 0
        
        # Combine canvas and camera feed
        img = cv2.add(img, canvas)
        
        # Show result
        cv2.imshow(window_name, img)
        
        # Quit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
