from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
# from handTrackingModule import handDetector
import mediapipe as mp
import time

def open_canvas():
    root.destroy()  # Destroy the main menu root
    canvas_root = Tk()
    canvas_root.attributes('-fullscreen', True)
    app = CanvasApp(canvas_root)
    canvas_root.mainloop()

def open_camera():
    root.destroy()  # Destroy the main menu root
    camera_root = Tk()
    camera_root.attributes('-fullscreen', True)
    app = FullScreenCameraApp(camera_root, "GUI\\header_def.jpg")

    def back_to_main():
        camera_root.destroy()
        open_main_menu()  # Call function to create new main menu

    app.exit_button.config(command=back_to_main)
    camera_root.mainloop()

def open_main_menu():  # Added this function
    global root  # Make root global so main function can access it
    root = Tk()
    root.attributes('-fullscreen', True)
    app = MainMenu(root)
    root.mainloop()

class CanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Canvas")
        Label(root, text="Canvas Area", font=("Arial", 36)).pack(pady=20)
        self.canvas_width = root.winfo_screenwidth()
        self.canvas_height = root.winfo_screenheight() - 180
        self.canvas = Canvas(root, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(pady=10)

        self.setup_buttons()

        # Initialize camera for hand detection
        self.cap = cv2.VideoCapture(0)
        self.detector = handDetector()

        # Previous point coordinates
        self.px, self.py = 0, 0

        # Current brush settings
        self.line_width = 15
        self.color = "black"

        # Start painting
        self.start_painting()

    def setup_buttons(self):
        # Button Frame for camera controls
        self.button_frame = Frame(self.root, bg="gray")
        self.button_frame.pack(fill=X, side=BOTTOM, pady=10)

        # Eraser toggle button
        self.eraser_button = Button(self.button_frame, text="Toggle Eraser", command=self.toggle_eraser, bg="black", fg="white", font=('Arial', 14), padx=20)
        self.eraser_button.pack(side=LEFT, padx=10)

        # Color buttons
        self.red_button = Button(self.button_frame, text="Red", command=lambda: self.set_brush_color("red"), bg="red", fg="white", font=('Arial', 14), padx=20)
        self.red_button.pack(side=LEFT, padx=5)

        self.green_button = Button(self.button_frame, text="Green", command=lambda: self.set_brush_color("green"), bg="green", fg="white", font=('Arial', 14), padx=20)
        self.green_button.pack(side=LEFT, padx=5)

        self.blue_button = Button(self.button_frame, text="Blue", command=lambda: self.set_brush_color("blue"), bg="blue", fg="white", font=('Arial', 14), padx=20)
        self.blue_button.pack(side=LEFT, padx=5)

        # Exit button
        self.exit_button = Button(self.button_frame, text="Exit", command=self.back_to_main, bg="red", fg="white", font=('Arial', 14), padx=20)
        self.exit_button.pack(side=RIGHT, padx=10)

    def set_brush_color(self, color):
        self.color = color

    def toggle_eraser(self):
        self.color = "white" if self.color != "white" else "black"

    def start_painting(self):
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

                # Map coordinates to canvas dimensions
                frame_height, frame_width, _ = img.shape
                mapped_x = int(x / frame_width * self.canvas_width)
                mapped_y = int(y / frame_height * self.canvas_height)

                # Set thickness
                thickness = 50 if self.color == "white" else 5
                paint_color = "white" if self.color == "white" else self.color

                # Draw line on the canvas with detected hand position
                if self.px == 0 and self.py == 0:
                    self.px, self.py = mapped_x, mapped_y
                else:
                    self.canvas.create_line(self.px, self.py, mapped_x, mapped_y,
                                            width=thickness, fill=paint_color,
                                            capstyle=ROUND, smooth=TRUE, splinesteps=36)

                # Update previous point
                self.px, self.py = mapped_x, mapped_y
            else:
                # Reset previous point when hand not detected
                self.px, self.py = 0, 0

            # Resize frame to fit GUI window
            img = cv2.resize(img, (self.canvas.winfo_width(), self.canvas.winfo_height()))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.canvas.create_image(0, 0, image=imgtk, anchor=NW)

            # Continue updating the frame
            self.root.after(10, self.update_frame)

    def stop_painting(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def back_to_main(self):
        self.root.destroy()
        open_main_menu()

class FullScreenCameraApp:
    def __init__(self, root, header_path):
        self.root = root
        self.root.title("Camera Viewer")

        # Set the window size to 640x480
        self.root.geometry("640x480")

        # Frame for video (taking up the remaining space)
        self.video_frame = Label(root, bg="black", height=280)  # Adjust the height to fit the remaining space (480 - 100 - 100)
        self.video_frame.pack(fill=BOTH, expand=True)

        # Frame for buttons (at the bottom)
        self.button_frame = Frame(root, bg="gray")
        self.button_frame.pack(fill=X, side=BOTTOM, pady=10)

        # Eraser toggle button
        self.eraser_button = Button(self.button_frame, text="Toggle Eraser", command=self.toggle_eraser, bg="black", fg="white", font=('Arial', 14), padx=20)
        self.eraser_button.pack(side=LEFT, padx=10)

        # Color buttons
        self.red_button = Button(self.button_frame, text="Red", command=lambda: self.change_color((0, 0, 255)), bg="red", fg="white", font=('Arial', 14), padx=20)
        self.red_button.pack(side=LEFT, padx=5)

        self.green_button = Button(self.button_frame, text="Green", command=lambda: self.change_color((0, 255, 0)), bg="green", fg="white", font=('Arial', 14), padx=20)
        self.green_button.pack(side=LEFT, padx=5)

        self.blue_button = Button(self.button_frame, text="Blue", command=lambda: self.change_color((255, 0, 0)), bg="blue", fg="white", font=('Arial', 14), padx=20)
        self.blue_button.pack(side=LEFT, padx=5)

        # Exit button
        self.exit_button = Button(self.button_frame, text="Exit", command=self.close_app, bg="red", fg="white", font=('Arial', 14), padx=20)
        self.exit_button.pack(side=RIGHT, padx=10)

        # Initialize VirtualPainter
        self.virtual_painter = VirtualPainter(root, self.video_frame)
        self.virtual_painter.start_painting_cam()  # Start painting functionality

    def toggle_eraser(self):
        self.virtual_painter.toggle_eraser()

    def change_color(self, color):
        self.virtual_painter.change_color(color)

    def close_app(self):
        # Stop virtual painter and close application
        self.virtual_painter.stop_painting()
        self.root.destroy()

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

        # Current color
        self.current_color = (0, 0, 255)  # Default to red

    def toggle_eraser(self):
        # Toggle eraser mode
        self.is_eraser = not self.is_eraser

    def change_color(self, color):
        # Change current drawing color
        self.current_color = color
        self.is_eraser = False  # Disable eraser when changing color

    def start_painting(self):
        if not self.running:
            self.running = True
            self.update_frame()

    def start_painting_cam(self):
        if not self.running:
            self.running = True
            self.update_frame_cam()

    def update_frame(self):
        if self.running:
            success, img = self.cap.read()
            if not success:
                self.stop_painting()
                return

            img = cv2.flip(img, 1)  # Mirror image

            # Detect hand landmarks
            img = self.detector.findHands(img)
            lm_list = self.detector.findPosition(img, draw=False)

            if len(lm_list) > 0:
                # Index finger coordinates
                x, y = lm_list[8][1], lm_list[8][2]

                # Smooth coordinates
                self.smoothed_x = 0.7 * getattr(self, 'smoothed_x', x) + 0.3 * x
                self.smoothed_y = 0.7 * getattr(self, 'smoothed_y', y) + 0.3 * y
                x, y = int(self.smoothed_x), int(self.smoothed_y)

                # Set thickness and color
                thickness = 50 if self.is_eraser else 15
                color = (0, 0, 0) if self.is_eraser else self.current_color

                # Draw line if not the first point
                if abs(x - self.px) > 5 or abs(y - self.py) > 5:  # Ignore small movements
                    if self.px != 0 and self.py != 0:
                        cv2.line(self.canvas, (self.px, self.py), (x, y), color, thickness)
                    self.px, self.py = x, y
            else:
                self.px, self.py = 0, 0  # Hand not detected

            # Create a white background
            white_background = np.ones_like(self.canvas, dtype=np.uint8) * 255
            combined_canvas = cv2.addWeighted(self.canvas, 1.0, white_background, 1.0, 0)

            # Render resized frame for display
            img = cv2.resize(combined_canvas, (self.video_label.winfo_width(), self.video_label.winfo_height()))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            # Schedule the next update
            self.root.after(15, self.update_frame)

    def update_frame_cam(self):
        if self.running:
            success, img = self.cap.read()
            if not success:
                self.stop_painting()
                return

            img = cv2.flip(img, 1)  # Mirror image

            # Detect hand landmarks
            img = self.detector.findHands(img)
            lm_list = self.detector.findPosition(img, draw=False)

            if len(lm_list) > 0:
                # Index finger coordinates
                x, y = lm_list[8][1], lm_list[8][2]

                # Smooth coordinates
                self.smoothed_x = 0.7 * getattr(self, 'smoothed_x', x) + 0.3 * x
                self.smoothed_y = 0.7 * getattr(self, 'smoothed_y', y) + 0.3 * y
                x, y = int(self.smoothed_x), int(self.smoothed_y)

                # Set thickness and color
                thickness = 50 if self.is_eraser else 15
                color = (0, 0, 0) if self.is_eraser else self.current_color

                # Draw line if movement is significant
                if abs(x - self.px) > 5 or abs(y - self.py) > 5:
                    if self.px != 0 and self.py != 0:
                        # Draw on both canvas and live feed
                        cv2.line(self.canvas, (self.px, self.py), (x, y), color, thickness)
                        cv2.line(img, (self.px, self.py), (x, y), color, thickness)
                    self.px, self.py = x, y
            else:
                # Reset previous points when hand is not detected
                self.px, self.py = 0, 0

            # Combine live video with the drawing canvas
            img = cv2.add(img, self.canvas)

            # Resize frame to fit the GUI window
            img = cv2.resize(img, (self.video_label.winfo_width(), self.video_label.winfo_height()))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Convert frame to Tkinter-compatible format
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            # Schedule the next frame update
            self.root.after(15, self.update_frame_cam)

    def stop_painting(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.canvas = np.zeros((480, 640, 3), np.uint8)

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Menggambar & Menulis")
        root.attributes('-fullscreen', True)
        main_frame = Frame(root)
        main_frame.pack(expand=True)

        Label(main_frame, text="Aplikasi Menggambar & Menulis", font=("Arial", 48)).pack(pady=(0, 40))

        Button(main_frame, text="Papan Tulis", command=open_canvas, bg="blue", fg="white", font=("Arial", 24), padx=20, pady=10).pack(pady=(0, 20))
        Button(main_frame, text="Papan Virtual", command=open_camera, bg="green", fg="white", font=("Arial", 24), padx=20, pady=10).pack(pady=(0, 0))

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5,modelComplexity=1,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils # it gives small dots onhands total 20 landmark points

    def findHands(self,img,draw=True):
        # Send rgb image to hands
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB) # process the frame
    #     print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    #Draw dots and connect them
                    self.mpDraw.draw_landmarks(img,handLms,self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self,img, handNo=0, draw=True):
        """Lists the position/type of landmarks
        we give in the list and in the list ww have stored
        type and position of the landmarks.
        List has all the lm position"""

        lmlist = []

        # check wether any landmark was detected
        if self.results.multi_hand_landmarks:
            #Which hand are we talking about
            myHand = self.results.multi_hand_landmarks[handNo]
            # Get id number and landmark information
            for id, lm in enumerate(myHand.landmark):
                # id will give id of landmark in exact index number
                # height width and channel
                h,w,c = img.shape
                #find the position
                cx,cy = int(lm.x*w), int(lm.y*h) #center
                # print(id,cx,cy)
                lmlist.append([id,cx,cy])

                # Draw circle for 0th landmark
                if draw:
                    cv2.circle(img,(cx,cy), 15 , (255,0,255), cv2.FILLED)

        return lmlist

def main():
    #Frame rates
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success,img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img,str(int(fps)),(10,70), cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

        cv2.imshow("Video",img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    open_main_menu()