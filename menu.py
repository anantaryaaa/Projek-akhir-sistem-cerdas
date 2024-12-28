from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
from handTrackingModule import handDetector

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
        self.line_width = 5
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
        self.virtual_painter = VirtualPainter2(root, self.video_frame)
        self.virtual_painter.start_painting()  # Start painting functionality

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
                color = (0, 0, 0) if self.is_eraser else self.current_color

                # Draw line if not the first point
                if self.px == 0 and self.py == 0:
                    self.px, self.py = x, y
                else:
                    # Draw on the canvas
                    cv2.line(self.canvas, (self.px, self.py), (x, y), color, thickness)

                # Update previous point
                self.px, self.py = x, y
            else:
                # Reset previous point when hand not detected
                self.px, self.py = 0, 0

            # Create a solid white background
            white_background = np.ones_like(self.canvas, dtype=np.uint8) * 255

            # Combine white background with the canvas (to ensure the drawing is on top of white)
            combined_canvas = cv2.addWeighted(self.canvas, 1.0, white_background, 1.0, 0)

            # Draw the latest strokes directly on top of the combined image
            if len(lm_list) > 0 and self.px != 0 and self.py != 0:
                cv2.line(combined_canvas, (self.px, self.py), (lm_list[8][1], lm_list[8][2]), color, thickness)

            # Resize frame to fit GUI window
            img = cv2.resize(combined_canvas, (self.video_label.winfo_width(), self.video_label.winfo_height()))
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

class VirtualPainter2:
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
                color = (0, 0, 0) if self.is_eraser else self.current_color

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

def open_main_menu():  # Added this function
    global root  # Make root global so main function can access it
    root = Tk()
    root.attributes('-fullscreen', True)
    app = MainMenu(root)
    root.mainloop()

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Menggambar & Menulis")
        root.attributes('-fullscreen', True)
        main_frame = Frame(root)
        main_frame.pack(expand=True)

        Label(main_frame, text="Main Menu", font=("Arial", 48)).pack(pady=(0, 40))

        Button(main_frame, text="Canvas", command=open_canvas, bg="blue", fg="white", font=("Arial", 24), padx=20, pady=10).pack(pady=(0, 20))
        Button(main_frame, text="Camera", command=open_camera, bg="green", fg="white", font=("Arial", 24), padx=20, pady=10).pack(pady=(0, 0))

if __name__ == "__main__":
    open_main_menu()