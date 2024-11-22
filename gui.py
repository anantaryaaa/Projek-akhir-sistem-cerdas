import cv2
from tkinter import *
from PIL import Image, ImageTk

class FullScreenCameraApp:
    def __init__(self, root, header_path):
        self.root = root
        self.root.title("Full Screen Camera Viewer")
        
        # Membuat layout full screen
        self.root.attributes('-fullscreen', True)

        # Menambahkan header
        self.header_img = Image.open(header_path)
        self.header_img = self.header_img.resize((self.root.winfo_screenwidth(), 100))  # Resize header sesuai layar
        self.header_photo = ImageTk.PhotoImage(self.header_img)

        self.header_label = Label(root, image=self.header_photo)
        self.header_label.pack()

        # Frame untuk video
        self.video_frame = Label(root, bg="black")
        self.video_frame.pack(fill=BOTH, expand=True)

        # Tombol untuk keluar
        self.exit_button = Button(root, text="Exit", command=self.close_app, bg="red", fg="white")
        self.exit_button.pack(side=BOTTOM, pady=10)

        self.running = False
        self.cap = None

        # Memulai kamera secara otomatis
        self.start_camera()

    def start_camera(self):
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)  # Membuka kamera (0 untuk webcam utama)
            self.update_frame()

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                # Resize frame ke layar penuh
                frame = cv2.resize(frame, (self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Konversi ke RGB
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_frame.imgtk = imgtk
                self.video_frame.config(image=imgtk)

            # Lanjutkan pembaruan frame
            self.root.after(10, self.update_frame)

    def close_app(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

# Main
header_path = "D:\\GUI Sisdas\\header.jpg"  # Path gambar header sesuai dengan lokasi file Anda
root = Tk()
app = FullScreenCameraApp(root, header_path)
root.mainloop()

