from tkinter import *
from PIL import Image, ImageTk
from virtualPainter import VirtualPainter  # Import the VirtualPainter class

class FullScreenCameraApp:
    def __init__(self, root, header_path):
        self.root = root
        self.root.title("Camera Viewer")

        # Set the window size to 640x480
        self.root.geometry("640x480")

        # Add header
        self.header_img = Image.open(header_path)
        self.header_img = self.header_img.resize((640, 100))  # Resize header to 640px width
        self.header_photo = ImageTk.PhotoImage(self.header_img)

        self.header_label = Label(root, image=self.header_photo)
        self.header_label.pack()

        # Frame for video (taking up the remaining space)
        self.video_frame = Label(root, bg="black", height=280)  # Adjust the height to fit the remaining space (480 - 100 - 100)
        self.video_frame.pack(fill=BOTH, expand=True)

        # Frame for buttons (at the bottom)
        self.button_frame = Frame(root, bg="gray")
        self.button_frame.pack(fill=X, side=BOTTOM, pady=10)

        # Eraser toggle button
        self.eraser_button = Button(self.button_frame, text="Toggle Eraser", command=self.toggle_eraser, bg="blue", fg="white")
        self.eraser_button.pack(side=LEFT, padx=10)

        # Exit button
        self.exit_button = Button(self.button_frame, text="Exit", command=self.close_app, bg="red", fg="white")
        self.exit_button.pack(side=RIGHT, padx=10)

        # Initialize VirtualPainter
        self.virtual_painter = VirtualPainter(root, self.video_frame)
        self.virtual_painter.start_painting()  # Start painting functionality

    def toggle_eraser(self):
        self.virtual_painter.toggle_eraser()

    def close_app(self):
        # Stop virtual painter and close application
        self.virtual_painter.stop_painting()
        self.root.destroy()

# Main
if __name__ == "__main__":
    header_path = "Header\\1.jpg"  # Update with the correct path to your header image
    root = Tk()
    app = FullScreenCameraApp(root, header_path)
    root.mainloop()
