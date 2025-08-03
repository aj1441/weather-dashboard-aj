from pathlib import Path
from itertools import cycle
from PIL import Image, ImageTk, ImageSequence
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, SUCCESS, WARNING, DANGER, INFO, LEFT, RIGHT, TOP, BOTTOM, BOTH

class ConfettiGif(tb.Frame):
    def __init__(self, master, gif_path="assets/gifs/confetti.gif", width=600, height=400, duration=5000):
        super().__init__(master, width=width, height=height)
        self.place(relx=0.5, rely=0.5, anchor="center")  # center overlay
        self.master = master

        # Load GIF and create loop iterator
        file_path = Path(gif_path)
        with Image.open(file_path) as im:
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s.convert("RGBA")) for s in sequence]
            self.image_cycle = cycle(images)
            self.framerate = im.info.get("duration", 100)

        self.img_label = tb.Label(self, image=next(self.image_cycle))
        self.img_label.pack(fill="both", expand="yes")

        self.running = True
        self.after(self.framerate, self.next_frame)

        # Optional auto-destroy after `duration` ms
        if duration:
            self.after(duration, self.destroy)

    def next_frame(self):
        if self.running:
            self.img_label.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)

    def destroy(self):
        self.running = False
        super().destroy()
