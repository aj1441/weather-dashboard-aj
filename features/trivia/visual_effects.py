# trivia/visual_effects.py

from pathlib import Path
from itertools import cycle
from PIL import Image, ImageTk, ImageSequence
import ttkbootstrap as tb
import tkinter as tk
import random

class ConfettiGif(tb.Frame):
    def __init__(self, master, gif_path="assets/confetti.gif", width=600, height=400, duration=5000):
        super().__init__(master, width=width, height=height)
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.master = master

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

        if duration:
            self.after(duration, self.destroy)

    def next_frame(self):
        if self.running:
            self.img_label.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)

    def destroy(self):
        self.running = False
        super().destroy()


class LightningEffect(tb.Frame):
    def __init__(self, master, duration=1000):
        super().__init__(master)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.flash_and_strike()
        self.after(duration, self.destroy)

    def flash_and_strike(self):
        self.canvas.configure(bg="white")
        self.after(100, lambda: self.canvas.configure(bg="black"))
        self.draw_lightning()

    def draw_lightning(self):
        x = random.randint(100, 500)
        y = 0
        segments = []
        for _ in range(10):
            new_x = x + random.randint(-20, 20)
            new_y = y + random.randint(20, 40)
            segments.append((x, y, new_x, new_y))
            x, y = new_x, new_y

        for line in segments:
            self.canvas.create_line(*line, fill="yellow", width=2)
        self.after(300, self.canvas.delete, "all")


class LightningGif(tb.Frame):
    def __init__(self, master, gif_path="assets/purpleLightning.gif", width=800, height=600, duration=3000):
        super().__init__(master)
        # Position to cover most of the trivia tab
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.master = master

        try:
            file_path = Path(gif_path)
            with Image.open(file_path) as im:
                sequence = ImageSequence.Iterator(im)
                # Scale each frame to the desired size
                scaled_images = []
                for frame in sequence:
                    scaled_frame = frame.resize((width, height), Image.Resampling.LANCZOS)
                    scaled_images.append(ImageTk.PhotoImage(scaled_frame.convert("RGBA")))
                
                self.image_cycle = cycle(scaled_images)
                self.framerate = im.info.get("duration", 100)

            self.img_label = tb.Label(self, image=next(self.image_cycle))
            self.img_label.place(relx=0.5, rely=0.5, anchor="center")

            self.running = True
            self.after(self.framerate, self.next_frame)

            if duration:
                self.after(duration, self.destroy)
                
        except Exception as e:
            print(f"Error loading lightning gif: {e}")
            # Fallback to original lightning effect
            self.destroy()

    def next_frame(self):
        if self.running:
            self.img_label.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)

    def destroy(self):
        self.running = False
        super().destroy()