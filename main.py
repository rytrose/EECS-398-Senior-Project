import tkinter as tk
from tkinter import ttk
from chuck import *
import time
import random
import math
import threading
import os
import urllib.request, urllib.parse, json


MED_FONT = ("Verdana", "12")
LARGE_FONT = ("Verdana", "18")
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
                lbl - label to be updated
                pin - pin to read from
                updateInt - time (in sec) to refresh, assuming instantaneous IO reads
'''
class IOUpdateLabel(threading.Thread):
    def __init__(self, lbl, pin, updateInt):
        threading.Thread.__init__(self)
        self.lbl = lbl
        self.pin = pin
        self.updateInt = updateInt

    def run(self):
        # CONSTANTLY GET UPDATED VALUE FROM I/O
        while True:
            self.lbl.config(text="TODO")
            time.sleep(self.updateInt)

'''
    Weather Label Update Class
        Contains Yahoo! Weather code and updates weather every minute
            Inputs:
                weatherLbl - weather label to be updated
'''
class WeatherUpdateLabel(threading.Thread):
    def __init__(self, condLbl, tempLbl):
        threading.Thread.__init__(self)
        self.condLbl = condLbl
        self.tempLbl = tempLbl

    def run(self):
        # Initialize Yahoo! Weather
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid=2433149"
        yql_url = baseurl + urllib.parse.urlencode({'q':yql_query}) + "&format=json"

        while True:
            # Open URL and grab data
            result = urllib.request.urlopen(yql_url).read()
            data = json.loads(result)
            conditions = data['query']['results']['channel']['item']['condition']
            self.tempLbl.config(text=str(conditions['temp']) + "°F")
            self.condLbl.config(text=str(conditions['text']))
            time.sleep(60)

''''
    Landing Page
        Home page once the display enters user mode
'''
class LandingPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        title = ttk.Label(self, text="Lake Metroparks Farmpark\n           Solar Tracker", font=TITLE_FONT)
        title.grid(row=0, column=1, sticky="N", pady=(60, 0))

        weatherTitleLbl = ttk.Label(self, text="Weather for Kirtland, OH", font=LARGE_FONT)
        weatherTitleLbl.grid(row=1, column=1, sticky="N", pady=(40, 10))

        condLbl = ttk.Label(self, text="", font=LARGE_FONT)
        condLbl.grid(row=2, column=1, sticky="N", pady=10)

        tempLbl = ttk.Label(self, text="°F", font=LARGE_FONT)
        tempLbl.grid(row=3, column=1, sticky="N", pady=10)

        self.yahooAttr = tk.PhotoImage(file="yahooAttr.png")
        attrLbl = ttk.Label(self, image=self.yahooAttr)
        attrLbl.grid(row=4, column=1, sticky="N", pady=5)

        # update weather values
        weatherT = WeatherUpdateLabel(condLbl, tempLbl)
        weatherT.daemon = True
        weatherT.start()

        audioLbl = ttk.Label(self, text="Audio Experiments", font=MED_FONT)
        self.audioIcon = tk.PhotoImage(file="headphones.png")
        audioBtn = ttk.Button(self, image=self.audioIcon, command = lambda: controller.show_frame(AudioPage))
        audioLbl.grid(row=5, column=0, sticky="W", padx=(110, 0), pady=10)
        audioBtn.grid(row=6, column=0, sticky="W", padx=(80, 0), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=MED_FONT)
        self.batteryIcon = tk.PhotoImage(file="battery.png")
        batteryBtn = ttk.Button(self, image=self.batteryIcon, command = lambda: controller.show_frame(BatteryPage))
        batteryLbl.grid(row=5, column=2, sticky="E", padx=(0, 105), pady=10)
        batteryBtn.grid(row=6, column=2, sticky="E", padx=(0, 80), pady=(10, 40))

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

'''
    Audio Page
        Page for the audio experiments
'''
class AudioPage(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        audioTitle = ttk.Label(self, text = "Audio Experiments", font = TITLE_FONT)
        audioTitle.grid(row=0, column=1, sticky="N", pady=(60, 0))

        playLbl = ttk.Label(self, text="Play Audio", font=MED_FONT)
        self.playIcon = tk.PhotoImage(file="headphones.png")
        playBtn = ttk.Button(self, image=self.playIcon, command = self.play)
        playLbl.grid(row=1, column=0, pady=(60, 0))
        playBtn.grid(row=2, column=0, pady=(10, 40))

        stopLbl = ttk.Label(self, text="Stop Audio", font=MED_FONT)
        self.stopIcon = tk.PhotoImage(file="headphones.png")
        stopBtn = ttk.Button(self, image=self.stopIcon, command = self.stop)
        stopLbl.grid(row=1, column=2, pady=(60, 0))
        stopBtn.grid(row=2, column=2, pady=(10, 40))

        homeLbl = ttk.Label(self, text="Back", font=MED_FONT)
        self.homeIcon = tk.PhotoImage(file="home.png")
        homeBtn = ttk.Button(self, image=self.homeIcon, command = lambda: controller.show_frame(LandingPage))
        homeLbl.grid(row=3, column=0, sticky="W", padx=(160, 20), pady=10)
        homeBtn.grid(row=4, column=0, sticky="W", padx=(80, 20), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=MED_FONT)
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
        # disable pitch class buttons
        # TODO

    # stops audio composition
    def stop(self):
        # stop audio
        self.playThread.stop()
        # disable pitch class buttons
        # TODO

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

        blues4 = ['C4', 'Ds4/Eb4', 'F4', 'Fs5/Gb5', 'G4', 'As4/Bb4', 'C5']
        pentatonic4 = ['C4', 'D4', 'E4', 'G4', 'A4', 'C5']
        self.pClass = blues4


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

        while True:
            # what will actually be playing
            while not self.stopped():
                # "read" current level
                curVal = math.floor(65535 * random.random())

                # set tempo
                self.beat = self.calcTempo(curVal)

                self.BeatsPerMeasure = 4

                # "read" voltage level
                volVal = math.floor(65535 * random.random())

                # calculate subdivisions
                self.calcSubdivisions(volVal, curVal)

                # use subdivisions to determine length of "measure" iteration
                self.measureCtr = ((self.BeatsPerMeasure/4) * self.numSubs)

                while self.measureCtr > 0:
                    volVal = math.floor(65535 * random.random())
                    s.setFrequency(self.myPitches[self.calcPitch(volVal)])
                    s.strike(0.5)
                    wait(self.wait)
                    self.measureCtr -= 1

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
        self.freq = self.myPitches[self.pClass[0]] + ((self.myPitches[self.pClass[len(self.myPitches) - 1]] - self.myPitches[self.pClass[0]]) * (val/65535))
        # return pitch in myPitches closest to freq
        return min(self.myPitches, key=lambda y:abs(float(self.myPitches[y]) - self.freq))

    def calcSubdivisions(self, volVal, curVal):
        MAX_PWR = 4294967296
        pwrVal = (volVal + 1) * (curVal + 1)
        # map "power" (i.e. the product of voltage and current values) [0 - 4294967296]
        if pwrVal > 0 and pwrVal < (MAX_PWR / 5):
            self.wait = 4 * self.beat
        elif pwrVal > (MAX_PWR / 5) and pwrVal < (2*(MAX_PWR / 5)):
            self.wait = 2 * self.beat
        elif pwrVal > (2*(MAX_PWR / 5)) and pwrVal < (3*(MAX_PWR / 5)):
            self.wait = self.beat
        elif pwrVal > (3*(MAX_PWR / 5)) and pwrVal < (4*(MAX_PWR / 5)):
            self.wait = (1/2) * self.beat
        elif pwrVal > (4*(MAX_PWR / 5)) and pwrVal < MAX_PWR:
            self.wait = (1/4) * self.beat
        else:
            self.wait = self.beat

        self.numSubs = 4 / (self.wait/self.beat)
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
