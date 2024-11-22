import cv2
import numpy as np
from handTrackingModule import handDetector
from PIL import Image, ImageTk

class VirtualPainter:
    def __init__(self, root, video_label):
        self.root = root
        self.video_label = video_label
        self.running = False

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.detector = handDetector()

        # Create canvas for drawing
        self.canvas = np.zeros((480, 640, 3), np.uint8)

        # Previous point coordinates
        self.px, self.py = 0, 0

        # Eraser mode
        self.is_eraser = False

    def toggle_eraser(self):
        # Toggle eraser mode
        self.is_eraser = not self.is_eraser

    def start_painting(self):
        if not self.running:
            self.running = True
            self.update_frame()

    def update_frame(self):
        if self.running:
            success, img = self.cap.read()
            if not success:
                self.stop_painting()
                return

            img = cv2.flip(img, 1)  # Mirror image

            # Find hand landmarks
            img = self.detector.findHands(img)
            lm_list = self.detector.findPosition(img, draw=False)

            if len(lm_list) > 0:  # If hand detected
                # Get index finger tip coordinates
                x, y = lm_list[8][1], lm_list[8][2]

                # Set thickness based on mode
                thickness = 50 if self.is_eraser else 15
                color = (0, 0, 0) if self.is_eraser else (0, 0, 255)

                # Draw line if not the first point
                if self.px == 0 and self.py == 0:
                    self.px, self.py = x, y
                else:
                    # Draw on both canvas and image
                    cv2.line(self.canvas, (self.px, self.py), (x, y), color, thickness)
                    cv2.line(img, (self.px, self.py), (x, y), color, thickness)

                # Update previous point
                self.px, self.py = x, y
            else:
                # Reset previous point when hand not detected
                self.px, self.py = 0, 0

            # Combine canvas and camera feed
            img = cv2.add(img, self.canvas)

            # Resize frame to fit GUI window
            img = cv2.resize(img, (self.video_label.winfo_width(), self.video_label.winfo_height()))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            # Continue updating the frame
            self.root.after(10, self.update_frame)

    def stop_painting(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.canvas = np.zeros((480, 640, 3), np.uint8)
