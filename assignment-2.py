import cv2
from tkinter import Tk, filedialog, Button, Scale, HORIZONTAL, Label, Frame, PhotoImage
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL
from functools import partial

class VideoPlayer:
    def __init__(self):
        self.root = Tk()
        self.root.title("Video Player")
        self.root.geometry("1920x1080")

        self.video_frame = Frame(self.root)
        self.video_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        self.video_label = Label(self.video_frame)
        self.video_label.pack(fill="both", expand=True)

        self.control_frame = Frame(self.root)
        self.control_frame.pack(side="right", padx=20, pady=20, fill="y")

        self.browse_button = Button(self.control_frame, text="Browse Video", command=self.browse_video, width=20)
        self.browse_button.pack(pady=10)

        self.camera_button = Button(self.control_frame, text="Camera Input", command=self.camera_input, width=20)
        self.camera_button.pack(pady=10)

        self.speed_slider = Scale(self.control_frame, from_=0.1, to=2.0, resolution=0.1, orient=HORIZONTAL,
                                  label="Playback Speed", command=self.set_speed, length=200)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=10)

        self.stop_button = Button(self.control_frame, text="Stop", command=self.stop, width=20)
        self.stop_button.pack(pady=10)

        self.resume_button = Button(self.control_frame, text="Resume", command=self.resume, width=20)
        self.resume_button.pack(pady=10)

        self.backward_button = Button(self.control_frame, text="<< Backward", command=partial(self.seek, -10), width=20)
        self.backward_button.pack(pady=10)

        self.forward_button = Button(self.control_frame, text="Forward >>", command=partial(self.seek, 10), width=20)
        self.forward_button.pack(pady=10)

        self.black_white_button = Button(self.control_frame, text="Black & White", command=self.convert_to_black_white, width=20)
        self.black_white_button.pack(pady=10)

        self.video_path = None
        self.cap = None
        self.playback_speed = 1.0
        self.paused = False

    def browse_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            self.play_video()

    def camera_input(self):
        self.cap = cv2.VideoCapture(0)
        self.play_video()

    def play_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.putText(frame, 'Playback Speed: {:.1f}x'.format(self.playback_speed), (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            self.update_video_label(frame)

            if not self.paused:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + self.playback_speed)

        if not self.paused:
            self.root.after(10, self.play_video)  # Schedule the next frame update after 10 milliseconds

    def update_video_label(self, frame):
        photo = self.convert_to_tkimage(frame)
        self.video_label.configure(image=photo)
        self.video_label.image = photo

    def set_speed(self, speed):
        self.playback_speed = float(speed)

    def stop(self):
        self.paused = True

    def resume(self):
        self.paused = False
        self.play_video()

    def seek(self, sec):
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        new_frame = current_frame + (sec * self.cap.get(cv2.CAP_PROP_FPS))
        if 0 <= new_frame <= total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def convert_to_black_white(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            self.update_video_label(frame)

    def convert_to_tkimage(self, frame):
        return PhotoImage(data=cv2.imencode('.png', frame)[1].tobytes())

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    player = VideoPlayer()
    player.run()
