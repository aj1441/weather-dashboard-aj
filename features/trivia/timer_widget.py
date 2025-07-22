# trivia/timer_widget.py

import ttkbootstrap as ttk
from ttkbootstrap.widgets import Meter
from ttkbootstrap.constants import *

class TimerWidget(ttk.Frame):
    def __init__(self, master, duration=20, callback=None):
        super().__init__(master)
        self.duration = duration
        self.remaining = duration
        self.callback = callback
        self.timer_running = False

        self.meter = Meter(
            self,
            bootstyle="info",
            amounttotal=self.duration,
            amountused=0,
            stripethickness=5,
            metertype="full",
            subtext="seconds left",
            subtextstyle="secondary",
            textright="s",
            textleft="Time"
        )
        self.meter.pack(fill=X, expand=YES, padx=10, pady=10)

    def start(self):
        self.remaining = self.duration
        self.timer_running = True
        self._tick()

    def _tick(self):
        if self.remaining <= 0:
            self.stop()
            if self.callback:
                self.callback()
            return

        if self.remaining <= 5:
            self.meter.configure(bootstyle="danger", subtextstyle="danger")
        elif self.remaining <= 10:
            self.meter.configure(bootstyle="warning", subtextstyle="warning")
        else:
            self.meter.configure(bootstyle="info", subtextstyle="secondary")

        self.meter.configure(amountused=self.duration - self.remaining)
        self.remaining -= 1
        self.after(1000, self._tick)

    def stop(self):
        self.timer_running = False
        self.meter.configure(amountused=self.duration)

    def reset(self):
        self.remaining = self.duration
        self.meter.configure(amountused=0)
        self.timer_running = False


# (To use inside TriviaTab)
# from features.trivia.timer_widget import TimerWidget
# timer = TimerWidget(master=self, duration=20, callback=handle_timeout)
# timer.start()
# timer.reset(), timer.stop()