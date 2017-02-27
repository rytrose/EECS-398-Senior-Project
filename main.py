import tkinter as tk
from tkinter import ttk
from chuck import *
import time
import random
import math
import threading
import os

LARGE_FONT = ("Verdana", "12")
TITLE_FONT = ("Verdana", "24")

# init ChucK
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
class IOUpdateLabel(threading.Thread):
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

''''
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
        t = IOUpdateLabel(test, 0.5)
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
        # pitch-to-freq dictionary
        self.p2f = { 'C2':65.41, 'Cs2/Db2':69.30, 'D2':73.42, 'Ds2/Eb2':77.78, 'E2':82.41,
'F2':87.31, 'Fs2/Gb2':92.50, 'G2':98.00, 'Gs2/Ab2':103.83, 'A2':110.00,
'As2/Bb2':116.54, 'B2':123.47, 'C3':130.81, 'Cs3/Db3':138.59, 'D3':146.83,
'Ds3/Eb3':155.56, 'E3':164.81, 'F3':174.61, 'Fs3/Gb3':185.00, 'G3':196.00,
'Gs3/Ab3':207.65, 'A3':220.00, 'As3/Bb3':233.08, 'B3':246.94, 'C4':261.63,
'Cs4/Db4':277.18, 'D4':293.66, 'Ds4/Eb4':311.13, 'E4':329.63, 'F4':349.23,
'Fs4/Gb4':369.99, 'G4':392.00, 'Gs4/Ab4':415.30, 'A4':440.00, 'As4/Bb4':466.16,
'B4':493.88, 'C5':523.25, 'Cs5/Db5':554.37, 'D5':587.33, 'Ds5/Eb5':622.25,
'E5':659.25, 'F5':698.46, 'Fs5/Gb5':739.99, 'G5':783.99, 'Gs5/Ab5':830.61,
'A5':880.00, 'As5/Bb5':932.33, 'B5':987.77, 'C6':1046.50 }

        self.pClass = ['C4', 'D4', 'E4', 'G4', 'A4', 'C5']

        # create dictionary of pitch frequencies I have chosen
        self.myPitches = self.p2f.fromkeys(self.pClass)
        for key in self.myPitches:
            self.myPitches[key] = self.p2f[key]

        # establish and connect instruments
        s = StruckBar()
        s.connect()
        s.setVolume(1.0)
        s.setStickHardness(0.1)
        s.setStrikePosition(0.1)
        s.preset(1)

        self.calcPitch(1)

        while True:
            # what will actually be playing
            while not self.stopped():
                curVal = math.floor(65535 * random.random())

                # set tempo
                self.beat = self.calcTempo(curVal)

                BeatsPerMeasure = 4
                while BeatsPerMeasure > 0:
                    volVal = math.floor(65535 * random.random())
                    s.setFrequency(self.myPitches[self.calcPitch(volVal)])
                    s.strike(0.5)
                    wait(self.beat)
                    BeatsPerMeasure -= 1

        # disconnect instruments
        s.disconnect()

    def calcTempo(self, val):
        # map incoming current values [0 - 65535]
        # to [1 - 0.25][sec]
        # or [60 BPM - 240 BPM]
        return 1 - ((val/65535) * 0.75)

    def calcPitch(self, val):
        # map incoming voltage values [0 - 65535]
        # to freq [variable based on myPitches range of freq]
        self.freq = 261.63 + (261.62 * (val/65535))
        # return pitch in myPitches closest to freq
        return min(self.myPitches, key=lambda y:abs(float(self.myPitches[y]) - self.freq))

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
