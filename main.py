import tkinter as tk
from tkinter import ttk
from chuck import *
import time
import random
import threading

LARGE_FONT = ("Verdana", "12")
TITLE_FONT = ("Verdana", "24")

# init chuck
init()

'''
    Main GUI Class
        Stores frames and starts app in fullscreen
'''
class DisplayApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = ttk.Frame(self)

        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0 , weight = 1)
        container.grid_columnconfigure(0 , weight = 1)

        # make app fullscreen
        self.state = True
        self.attributes("-fullscreen", self.state)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)

        self.frames = {}

        for F in (LandingPage, AudioPage, BatteryPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(LandingPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def toggle_fullscreen(self, event = None):
        self.state = not self.state
        self.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event = None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"

'''
    IO Label Update Class
        Allows for labels that update in response to IO
            Inputs:
                var - label to be updated
                updateInt - time (in sec) to refresh, assuming non-blocking IO reads
'''
class IOUpdate(threading.Thread):
    def __init__(self, var, updateInt):
        threading.Thread.__init__(self)
        self.var = var
        self.updateInt = updateInt

    def run(self):
        # CONSTANTLY GET UPDATED VALUE FROM I/O
        while True:
            # ADD GPIO ACCESS HERE
            self.var.config(text=str(random.random()))
            time.sleep(self.updateInt)

'''
    Landing Page
        Home page once the display enters user mode
'''
class LandingPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        title = ttk.Label(self, text="Lake Metroparks Farmpark\n           Solar Tracker", font=TITLE_FONT)
        title.grid(row=0, column=1, sticky="N", pady=(60, 0))

        test = ttk.Label(self, text = "0", font = LARGE_FONT)
        test.grid(row=1, column=1, sticky="N")

        # update I/O values
        t = IOUpdate(test, 0.5)
        t.daemon = True
        t.start()

        audioLbl = ttk.Label(self, text="Audio Experiments", font=LARGE_FONT)
        self.audioIcon = tk.PhotoImage(file="headphones.png")
        audioBtn = ttk.Button(self, image=self.audioIcon, command = lambda: controller.show_frame(AudioPage))
        audioLbl.grid(row=2, column=0, sticky="W", padx=(110, 0), pady=10)
        audioBtn.grid(row=3, column=0, sticky="W", padx=(80, 0), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=LARGE_FONT)
        self.batteryIcon = tk.PhotoImage(file="battery.png")
        batteryBtn = ttk.Button(self, image=self.batteryIcon, command = lambda: controller.show_frame(BatteryPage))
        batteryLbl.grid(row=2, column=2, sticky="E", padx=(0, 105), pady=10)
        batteryBtn.grid(row=3, column=2, sticky="E", padx=(0, 80), pady=(10, 40))

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

'''
    Audio Page
        Page for the audio experiments
'''
class AudioPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        audioTitle = ttk.Label(self, text = "Audio Experiments", font = TITLE_FONT)
        audioTitle.grid(row=0, column=1, sticky="N", pady=(60, 0))

        playLbl = ttk.Label(self, text="Play Audio", font=LARGE_FONT)
        self.playIcon = tk.PhotoImage(file="headphones.png")
        playBtn = ttk.Button(self, image=self.playIcon, command = self.play)
        playLbl.grid(row=1, column=0, pady=(60, 0))
        playBtn.grid(row=2, column=0, pady=(10, 40))

        stopLbl = ttk.Label(self, text="Stop Audio", font=LARGE_FONT)
        self.stopIcon = tk.PhotoImage(file="headphones.png")
        stopBtn = ttk.Button(self, image=self.stopIcon, command = self.stop)
        stopLbl.grid(row=1, column=2, pady=(60, 0))
        stopBtn.grid(row=2, column=2, pady=(10, 40))

        homeLbl = ttk.Label(self, text="Back", font=LARGE_FONT)
        self.homeIcon = tk.PhotoImage(file="home.png")
        homeBtn = ttk.Button(self, image=self.homeIcon, command = lambda: controller.show_frame(LandingPage))
        homeLbl.grid(row=3, column=0, sticky="W", padx=(160, 20), pady=10)
        homeBtn.grid(row=4, column=0, sticky="W", padx=(80, 20), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=LARGE_FONT)
        self.batteryIcon = tk.PhotoImage(file="battery.png")
        batteryBtn = ttk.Button(self, image=self.batteryIcon, command = lambda: controller.show_frame(BatteryPage))
        batteryLbl.grid(row=3, column=2, sticky="E", padx=(20, 105), pady=10)
        batteryBtn.grid(row=4, column=2, sticky="E", padx=(20, 80), pady=(10, 40))

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # create audio thread
        self.playThread = AudioPlayThread()
        self.playThread.daemon = True
        self.playThread.stop()
        self.playThread.start()

    # plays audio composition
    def play(self):
        # start audio
        self.playThread._stop.clear()

    # stops audio composition
    def stop(self):
        # stop audio
        self.playThread.stop()

'''
    Audio Play Thread
'''
class AudioPlayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        # establish and connect instruments
        s = StruckBar()
        s.setVolume(0.8)
        s.preset(1)
        s.connect()


        while True:
            # what will actually be playing
            while not self.stopped():
                s.strike(0.4)
                s.strike(0.8)
                wait(0.1)
                wait(0.1)
                s.strike(1.0)
                wait(0.5)

        # disconnect instruments
        s.disconnect()

'''
    Battery Page
        Page for the battery diagnostics
'''
class BatteryPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "Battery Diagnostics", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)

        landingBtn = ttk.Button(self, text = "Back to Landing", command = lambda: controller.show_frame(LandingPage))
        landingBtn.pack()

# run the app
app = DisplayApp()
app.geometry("1024x768")
app.mainloop()
