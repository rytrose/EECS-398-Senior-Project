#!/usr/bin/python3

# GUI imports
import tkinter as tk
from tkinter import ttk

# ChucK and music-utilized imports
from chuck import *

# used for sleeping
import time

import random
import math

# used for concurrency
import threading
import os

# used for I/O
import RPi.GPIO as GPIO

# used for weather data acquisition
import urllib.request, urllib.parse, json

# ADC import
import Adafruit_ADS1x15

# GPIO mode output pin
MODE_PIN = 26
GPIO.setmode(GPIO.BCM)

# setup pin 26 as output
GPIO.setup(MODE_PIN, GPIO.OUT)

# LOW = auto mode, HIGH = user mode
# default to auto mode
GPIO.output(MODE_PIN, GPIO.LOW)

# pitch set global variable and mutex
c = threading.Condition()
ps = 0

# Timer global variable and mutex
c1 = threading.Condition()
TIMEOUT = 120 # number of seconds before user goes to auto mode
timer = TIMEOUT

# setup ADC
adc = Adafruit_ADS1x15.ADS1115()

# ADC GAIN VALUES
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
GAIN = 1

# setup channels
VOLTAGE = 0
CURRENT = 1
BATTERY = 2

# setup fonts
SM_FONT = ("Verdana", "11")
MED_FONT = ("Verdana", "12")
ML_FONT = ("Verdana", "16")
LARGE_FONT = ("Verdana", "18")
XL_FONT = ("Verdana", "21")
TITLE_FONT = ("Verdana", "24")

# init ChucK
init()

# seed random
random.seed(None)

# Wait to ensure internet connection on boot
# time.sleep(10)

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

        for F in (AutoPage, LandingPage, AudioPage, BatteryPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(AutoPage)

    def show_frame(self, cont):
        self.resetTimer()
        if cont.__name__ != "AutoPage":
            print("Switching to user mode")
            GPIO.output(MODE_PIN, GPIO.HIGH)
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

    def resetTimer(self):
        # establish global timer variable
        global timer

        c1.acquire()
        timer = TIMEOUT
        c1.release()

''''
     Auto Page
        Welcome screen inviting users to tap, entering user mode
'''

class AutoPage(ttk.Frame):

    def __init__(self, parent, controller):
        gui_style = ttk.Style()
        gui_style.configure('My1.TFrame', background='#ffaaaa')
        gui_style.configure('My1.TLabel', background='#ffaaaa')

        ttk.Frame.__init__(self, parent, style="My1.TFrame")
        title = ttk.Label(self, text="Lake Metroparks Farmpark\n           Solar Tracker", font=TITLE_FONT, style="My1.TLabel")
        title.grid(row=1, column=1, sticky="N", pady=(80, 0))
        beginLbl = ttk.Label(self, text="Tap anywhere to begin!", font=MED_FONT, style="My1.TLabel")
        beginLbl.grid(row=2, column=1, pady=(10,40))

        self.fpLogoAttr = tk.PhotoImage(file="/home/pi/SPC/lake metroparks logo.png")
        fpLogoLbl = ttk.Label(self, image=self.fpLogoAttr, style="My1.TLabel")
        fpLogoLbl.grid(row=3, column=1, padx=40, pady=20)

        self.rwLogoAttr = tk.PhotoImage(file="/home/pi/SPC/Rockwell_Automation_logo.png")
        rwLogoLbl = ttk.Label(self, image=self.rwLogoAttr, style="My1.TLabel")
        rwLogoLbl.grid(row=5, column=2, sticky="E", padx=(80, 10), pady=(10, 10))

        self.cwruLogoAttr = tk.PhotoImage(file="/home/pi/SPC/cwru-formal-logo.png")
        cwruLogoLbl = ttk.Label(self, image=self.cwruLogoAttr, style="My1.TLabel")
        cwruLogoLbl.grid(row=5, column=0, sticky="W", padx=10, pady=(10, 10))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.bind("<Button-1>", lambda x: controller.show_frame(LandingPage))
        title.bind("<Button-1>", lambda x: controller.show_frame(LandingPage))
        beginLbl.bind("<Button-1>", lambda x: controller.show_frame(LandingPage))
        fpLogoLbl.bind("<Button-1>", lambda x: controller.show_frame(LandingPage))
        rwLogoLbl.bind("<Button-1>", lambda x: controller.show_frame(LandingPage))

        timerT = TimerThread(controller)
        timerT.daemon = True
        timerT.start()

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

        wait(10)

        while True:
            # Open URL and grab data
            result = urllib.request.urlopen(yql_url).read()
            data = json.loads(result.decode("utf-8"))
            conditions = data['query']['results']['channel']['item']['condition']
            self.tempLbl.config(text=str(conditions['temp']) + "°F")
            self.condLbl.config(text=str(conditions['text']))
            time.sleep(60)

'''
    Panel Label Update Class
        Updates the labels displaying live panel information
            Inputs:
                volLbl - voltage label to be updated
                curLbl - current label to be updated
                interval - interval of time between updates
'''
class PanelUpdateLabel(threading.Thread):
    def __init__(self, volLbl, curLbl, interval):
        threading.Thread.__init__(self)
        self.volLbl = volLbl
        self.curLbl = curLbl
        self.interval = interval

    def run(self):
        while True:
            volIn = adc.read_adc(VOLTAGE, gain=GAIN)
            curIn = adc.read_adc(CURRENT, gain=GAIN)

            print("Voltage Raw: " + str(volIn) + " | Current Raw: " + str(curIn))

            # maps [0 - 26500] to [0 - 10V] to [0 - 240V]
            volVal = ((volIn / 26500) * 10) * 24
            # maps [0 - 26500] to [4 - 20 mA] to [0 - 7A] 
            curVal = ((curIn / 26500) * 16) * .4375 

            self.volLbl.config(text=str(round(volVal, 4)) + " Volts")
            self.curLbl.config(text=str(round(curVal, 4)) + " Amps")
            time.sleep(self.interval)

''''
    Timer Thread
        Handles the timer between auto and user mode
'''
class TimerThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller

    def run(self):
        # Establish global timer variable
        global timer

        while True:
            c.acquire()
            if timer == 0:
                timer = TIMEOUT
                # set mode to auto mode
                print("Switching to auto mode")
                GPIO.output(MODE_PIN, GPIO.LOW)
                self.controller.show_frame(AutoPage)
            else:
                timer -= 1
                print("timer: " + str(timer))
            c.release()
            wait(1)


''''
    Landing Page
        Home page once the display enters user mode
'''
class LandingPage(ttk.Frame):

    def __init__(self, parent, controller):
        # background color
        gui_style = ttk.Style()
        gui_style.configure('My.TFrame', background='#e8feff')
        gui_style.configure('My.TLabel', background='#e8feff')
        gui_style.configure('My.TButton', background='#c6d2ff')

        # frame and title
        ttk.Frame.__init__(self, parent, style="My.TFrame")
        title = ttk.Label(self, text="Lake Metroparks Farmpark\n           Solar Tracker", font=TITLE_FONT, style="My.TLabel")
        title.grid(row=0, column=1, sticky="N", pady=(60, 0))

        # weather data display
        weatherTitleLbl = ttk.Label(self, text="Weather for Kirtland, OH", font=LARGE_FONT, style="My.TLabel")
        weatherTitleLbl.grid(row=1, column=1, sticky="N", pady=(40, 10))

        condLbl = ttk.Label(self, text="", font=LARGE_FONT, style="My.TLabel")
        condLbl.grid(row=2, column=1, sticky="N", pady=10)

        tempLbl = ttk.Label(self, text="°F", font=LARGE_FONT, style="My.TLabel")
        tempLbl.grid(row=3, column=1, sticky="N", pady=10)

        self.yahooAttr = tk.PhotoImage(file="/home/pi/SPC/yahooAttr.png")
        attrLbl = ttk.Label(self, image=self.yahooAttr, style="My.TLabel")
        attrLbl.grid(row=4, column=1, sticky="N", pady=5)

        # update weather values
        weatherT = WeatherUpdateLabel(condLbl, tempLbl)
        weatherT.daemon = True
        weatherT.start()

        # next page labels/buttons
        audioLbl = ttk.Label(self, text="Audio Experiments", font=MED_FONT, style="My.TLabel")
        self.audioIcon = tk.PhotoImage(file="/home/pi/SPC/headphones.png")
        audioBtn = ttk.Button(self, image=self.audioIcon, style="My.TButton", command = lambda: controller.show_frame(AudioPage))
        audioLbl.grid(row=5, column=0, sticky="W", padx=(110, 0), pady=(10, 0))
        audioBtn.grid(row=6, column=0, sticky="W", padx=(80, 0), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=MED_FONT, style="My.TLabel")
        self.batteryIcon = tk.PhotoImage(file="/home/pi/SPC/battery.png")
        batteryBtn = ttk.Button(self, image=self.batteryIcon, style="My.TButton", command = lambda: controller.show_frame(BatteryPage))
        batteryLbl.grid(row=5, column=2, sticky="E", padx=(0, 105), pady=(10, 0))
        batteryBtn.grid(row=6, column=2, sticky="E", padx=(0, 80), pady=(10, 40))

        # frame for panel values
        panelFrame = ttk.Frame(self, style="My.TFrame")
        panelFrame.grid(row=6, column=1, sticky="NSEW")

        # labels for panel values
        volDescLbl = ttk.Label(panelFrame, text="Voltage from Solar Panel", font=SM_FONT, style="My.TLabel")
        curDescLbl = ttk.Label(panelFrame, text="Amperage from Solar Panel", font=SM_FONT, style="My.TLabel")
        volLbl = ttk.Label(panelFrame, text=" Volts", font=MED_FONT, style="My.TLabel")
        curLbl = ttk.Label(panelFrame, text=" Amps", font=MED_FONT, style="My.TLabel")
        volDescLbl.grid(row=0, column=1)
        curDescLbl.grid(row=0, column=3)
        volLbl.grid(row=1, column=1, pady=(40, 0))
        curLbl.grid(row=1, column=3, pady=(40, 0))

        # panel grid weights for centering
        panelFrame.grid_columnconfigure(0, weight=1)
        panelFrame.grid_columnconfigure(2, weight=1)
        panelFrame.grid_columnconfigure(4, weight=1)

        # update panel values
        panelT = PanelUpdateLabel(volLbl, curLbl, 2)
        panelT.daemon = True
        panelT.start()

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # bind click to timer reset
        self.bind("<Button-1>", lambda x: self.resetTimer())

    def resetTimer(self):
        # establish global timer variable
        global timer

        c1.acquire()
        timer = TIMEOUT
        c1.release()


'''
    Audio Page
        Page for the audio experiments
'''
class AudioPage(ttk.Frame):

    def __init__(self, parent, controller):
        # background color
        gui_style = ttk.Style()
        gui_style.configure('My3.TFrame', background='#ffffba')
        gui_style.configure('My3.TLabel', background='#ffffba')
        gui_style.configure('My3.TButton', background='#c6d2ff')

        # frame
        ttk.Frame.__init__(self, parent, style="My3.TFrame")

        # title
        audioTitle = ttk.Label(self, text = "Audio Experiments", font = TITLE_FONT, style="My3.TLabel")
        audioTitle.grid(row=0, column=1, sticky="N", pady=(60, 0))

        # play/stop labels and buttons
        playLbl = ttk.Label(self, text="Play Audio", font=MED_FONT, style="My3.TLabel")
        self.playIcon = tk.PhotoImage(file="/home/pi/SPC/headphones.png")
        playBtn = ttk.Button(self, image=self.playIcon, style="My3.TButton", command = self.play)
        playLbl.grid(row=1, column=0, pady=(10, 0))
        playBtn.grid(row=2, column=0, pady=(10, 10))

        stopLbl = ttk.Label(self, text="Stop Audio", font=MED_FONT, style="My3.TLabel")
        self.stopIcon = tk.PhotoImage(file="/home/pi/SPC/headphones.png")
        stopBtn = ttk.Button(self, image=self.stopIcon, style="My3.TButton", command = self.stop)
        stopLbl.grid(row=1, column=2, pady=(10, 0))
        stopBtn.grid(row=2, column=2, pady=(10, 10))

        # next page labels/buttons
        homeLbl = ttk.Label(self, text="Back", font=MED_FONT, style="My3.TLabel")
        self.homeIcon = tk.PhotoImage(file="/home/pi/SPC/home.png")
        homeBtn = ttk.Button(self, image=self.homeIcon, style="My3.TButton", command = lambda: controller.show_frame(LandingPage))
        homeLbl.grid(row=4, column=0, sticky="W", padx=(160, 20), pady=(10, 0))
        homeBtn.grid(row=5, column=0, sticky="W", padx=(80, 20), pady=(10, 40))

        batteryLbl = ttk.Label(self, text="Battery Diagnostics", font=MED_FONT, style="My3.TLabel")
        self.batteryIcon = tk.PhotoImage(file="/home/pi/SPC/battery.png")
        batteryBtn = ttk.Button(self, image=self.batteryIcon, style="My3.TButton", command = lambda: controller.show_frame(BatteryPage))
        batteryLbl.grid(row=4, column=2, sticky="E", padx=(20, 105), pady=(10, 0))
        batteryBtn.grid(row=5, column=2, sticky="E", padx=(20, 80), pady=(10, 40))

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # embedded frame for panel stats
        pitchFrame = ttk.Frame(self, style="My3.TFrame")
        pitchFrame.grid(row=3, column=1, sticky="NSEW")

        self.pitchDescLbl = ttk.Label(pitchFrame, text="Change Pitch Set", font=MED_FONT, style="My3.TLabel")
        self.pitchBtnL = ttk.Button(pitchFrame, text="<--", style="My3.TButton", command = lambda: self.changePitches(0))
        self.pitchBtnR = ttk.Button(pitchFrame, text="-->", style="My3.TButton", command = lambda: self.changePitches(1))
        self.pitchLbl = ttk.Label(pitchFrame, text="Blues", font=MED_FONT, style="My3.TLabel")
        self.pitchDescLbl.grid(row=0, column=2, pady=(0, 5))
        self.pitchBtnL.grid(row=1, column=1)
        self.pitchLbl.grid(row=1, column=2, padx=15)
        self.pitchBtnR.grid(row=1, column=3)

        # panel frame grid weights for centering
        pitchFrame.grid_columnconfigure(0, weight=1)
        pitchFrame.grid_columnconfigure(4, weight=1)

        # create audio thread
        self.playThread = AudioPlayThread()
        self.playThread.daemon = True
        self.playThread.stop()
        self.playThread.start()

        # create pitch label thread
        self.pitchLblThread = PitchLabelUpdate(self.pitchLbl)
        self.pitchLblThread.daemon = True
        self.pitchLblThread.start()

        # bind click to timer reset
        self.bind("<Button-1>", lambda x: self.resetTimer())

    def resetTimer(self):
        # establish global timer variable
        global timer

        c1.acquire()
        timer = TIMEOUT
        c1.release()

    # changes the pitch set
    def changePitches(self, lr):
        self.resetTimer()

        # Establish global pitch set variable
        global ps

        c.acquire()
        if lr == 0:
            if ps > 0:
                ps -= 1
            else:
                ps = 2
        if lr == 1:
            if ps < 2:
                ps += 1
            else:
                ps = 0
        c.release()


    # plays audio composition
    def play(self):
        self.resetTimer()

        # disable change pitches
        self.pitchBtnL.state(["disabled"])
        self.pitchBtnR.state(["disabled"])
        # start audio
        self.playThread._stop.clear()

    # stops audio composition
    def stop(self):
        self.resetTimer()

        # enable change pitches
        self.pitchBtnL.state(["!disabled"])
        self.pitchBtnR.state(["!disabled"])
        # stop audio
        self.playThread.stop()

'''
    Pitch Label Update Class
        Allows for pitch label to be updated
            Inputs:
                pitchLbl - label to be updated
'''

class PitchLabelUpdate(threading.Thread):
    def __init__(self, pitchLbl):
        threading.Thread.__init__(self)
        self.pitchLbl = pitchLbl

    def run(self):
        # Establish global pitch set variable
        global ps

        while True:
            c.acquire()
            if ps == 0:
                self.pitchLbl.config(text="Blues")
            elif ps == 1:
                self.pitchLbl.config(text="Pentatonic")
            elif ps == 2:
                self.pitchLbl.config(text="Wholetone")
            else:
                self.pitchLbl.config(text="ERROR")
            c.release()
            wait(0.11)

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
        # setup global pitch set variable
        global ps

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

        blues = ['C2', 'Ds2/Eb2', 'F2', 'Fs2/Gb2', 'G2', 'As2/Bb2', 'C3', 'Ds3/Eb3', 'F3', 'Fs3/Gb3', 'G3', 'As3/Bb3', 'C4', 'Ds4/Eb4', 'F4', 'Fs4/Gb4', 'G4', 'As4/Bb4', 'C5']
        pentatonic = ['C2', 'D2', 'E2', 'G2', 'A2', 'C3', 'D3', 'E3', 'G3', 'A3', 'C4', 'D4', 'E4', 'G4', 'A4', 'C5']
        wholetone = ['C2', 'D2', 'E2', 'Fs2/Gb2', 'Gs2/Ab2', 'As2/Bb2', 'C3', 'D3', 'E3', 'Fs3/Gb3', 'Gs3/Ab3', 'As3/Bb3', 'C4', 'D4', 'E4', 'Fs4/Gb4', 'Gs4/Ab4', 'As4/Bb4', 'C5']

        # default
        self.pClass = blues

        # create dictionary of pitch frequencies
        self.myPitches = self.p2f.fromkeys(self.pClass)
        for key in self.myPitches:
            self.myPitches[key] = self.p2f[key]
        # create lists for order
        self.pitchList = list(self.myPitches.keys())
        self.freqList = list(self.myPitches.values())

        # establish and connect instruments
        s = StruckBar()
        s.connect()
        s.setVolume(1.0)         # 0.0 <= volume <= 1.0
        s.setStickHardness(0.1)  # 0.0 <= hardness <= 1.0
        s.setStrikePosition(0.1) # 0.0 <= position <= 1.0
        s.preset(1)              # vibraphone

        while True:
            c.acquire()
            if ps == 0:
                self.pClass = blues
            elif ps == 1:
                self.pClass = pentatonic
            elif ps == 2:
                self.pClass = wholetone
            else:
                self.pClass = ['C4']
            c.release()
            wait(0.1)

            # recreate dictionary of pitch frequencies
            self.myPitches = self.p2f.fromkeys(self.pClass)
            for key in self.myPitches:
                self.myPitches[key] = self.p2f[key]
            # create lists for order
            self.pitchList = list(self.myPitches.keys())
            self.freqList = list(self.myPitches.values())

            # what will actually be playing
            while not self.stopped():
                # read current level
                curVal = adc.read_adc(CURRENT, gain=GAIN)
                
                # set tempo
                self.beat = self.calcTempo(curVal)

                self.BeatsPerMeasure = 4

                # read voltage level
                volVal = adc.read_adc(VOLTAGE, gain=GAIN)
                
                # calculate subdivisions
                self.calcSubdivisions(volVal, curVal)

                # use subdivisions to determine length of "measure" iteration
                self.measureCtr = ((self.BeatsPerMeasure/4) * self.numSubs)

                while self.measureCtr > 0:
                    # determine notes
                    mainPitch = self.calcPitch(volVal)
                    secPitch = None
                    terPitch = None
                    mainIndex = self.pitchList.index(mainPitch)
                    if mainIndex > 0 and mainIndex < (len(self.pitchList) - 1):
                        secPitch = self.pitchList[mainIndex - 1]
                        terPitch = self.pitchList[mainIndex + 1]
                    elif mainIndex == 0:
                        secPitch = self.pitchList[mainIndex + 1]
                        terPitch = self.pitchList[mainIndex + 2]
                    elif mainIndex == (len(self.pitchList) - 1):
                        secPitch = self.pitchList[mainIndex - 1]
                        terPitch = self.pitchList[mainIndex - 2]

                    # choose note
                    rand = random.random()
                    if rand > 0.0 and rand < 0.15:
                        s.setFrequency(self.myPitches[secPitch])
                        print("played sec")
                    elif rand >= 0.15 and rand <= 0.85:
                        s.setFrequency(self.myPitches[mainPitch])
                        print("played main")
                    else:
                        s.setFrequency(self.myPitches[terPitch])
                        print("played ter")

                    s.strike(0.5)
                    wait(self.wait)
                    self.measureCtr -= 1

        # disconnect instruments
        s.disconnect()

    def calcTempo(self, val):
        # map incoming current values [0 - 27000]
        # to [1 - 0.3][sec]
        # or [60 - 200] [BPM]
        return 1 - ((val/27000) * 0.7)

    def calcPitch(self, val):
        # map incoming voltage values [0 - 27000]
        # to freq [variable based on myPitches range of freq]
        self.freq = self.myPitches[self.pClass[0]] + ((self.myPitches[self.pClass[len(self.myPitches) - 1]] - self.myPitches[self.pClass[0]]) * (val/27000))
        # return pitch in myPitches closest to freq
        pitch = min(self.myPitches, key=lambda y:abs(float(self.myPitches[y]) - self.freq))
        return pitch

    def calcSubdivisions(self, volVal, curVal):
        MAX_PWR = 27000 * 27000
        PWR_DIV = MAX_PWR / 5
        pwrVal = (volVal + 1) * (curVal + 1)
        # map "power" (i.e. the product of voltage and current values) [0 - 25000 * 25000]
        if pwrVal > 0 and pwrVal < (MAX_PWR / 5):
            self.wait = 4 * self.beat
        elif pwrVal > PWR_DIV and pwrVal < (2*PWR_DIV):
            self.wait = 2 * self.beat
        elif pwrVal > (2*PWR_DIV) and pwrVal < (3*PWR_DIV):
            self.wait = self.beat
        elif pwrVal > (3*PWR_DIV) and pwrVal < (4*PWR_DIV):
            self.wait = (1/2) * self.beat
        elif pwrVal > (4*PWR_DIV) and pwrVal < MAX_PWR:
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
        # background color
        gui_style = ttk.Style()
        gui_style.configure('My2.TFrame', background='#b3ffb2')
        gui_style.configure('My2.TLabel', background='#b3ffb2')
        gui_style.configure('My2.TButton', background='#c6d2ff')

        # frame and title
        ttk.Frame.__init__(self, parent, style="My2.TFrame")
        title = ttk.Label(self, text="Battery Diagnostics", font=TITLE_FONT, style="My2.TLabel")
        title.grid(row=0, column=1, sticky="N", pady=(60, 0))

        # next page labels/buttons
        homeLbl = ttk.Label(self, text="Back", font=MED_FONT, style="My2.TLabel")
        self.homeIcon = tk.PhotoImage(file="/home/pi/SPC/home.png")
        homeBtn = ttk.Button(self, image=self.homeIcon, style="My2.TButton", command = lambda: controller.show_frame(LandingPage))
        homeLbl.grid(row=7, column=0, sticky="W", padx=(160, 20), pady=(10, 0))
        homeBtn.grid(row=8, column=0, sticky="W", padx=(80, 20), pady=(10, 40))

        audioLbl = ttk.Label(self, text="Audio Experiments", font=MED_FONT, style="My2.TLabel")
        self.audioIcon = tk.PhotoImage(file="/home/pi/SPC/headphones.png")
        audioBtn = ttk.Button(self, image=self.audioIcon, style="My2.TButton", command = lambda: controller.show_frame(AudioPage))
        audioLbl.grid(row=7, column=2, sticky="E", padx=(20, 105), pady=(10, 0))
        audioBtn.grid(row=8, column=2, sticky="E", padx=(20, 80), pady=(10, 40))

        # battery diagnostic labels
        chargingLbl = ttk.Label(self, text="Not Charging", font=LARGE_FONT, style="My2.TLabel")
        chargingLbl.grid(row=2, column=1, pady=(5, 40))
        pwrConsumptionLbl = ttk.Label(self, text="Battery Power Consumption", font=LARGE_FONT, style="My2.TLabel")
        pwrConsumptionLbl.grid(row=3, column=1, pady=5)
        powerLbl = ttk.Label(self, text="0 mAh", font=ML_FONT, style="My2.TLabel")
        powerLbl.grid(row=4, column=1, pady=5)
        timeLbl = ttk.Label(self, text="", font=ML_FONT, style="My2.TLabel")
        timeLbl.grid(row=5, column=1, pady=5)

        # grid weights for centering
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # update battery values
        batteryT = BatteryUpdateLabel(chargingLbl, powerLbl, timeLbl)
        batteryT.daemon = True
        batteryT.start()

        # bind click to timer reset
        self.bind("<Button-1>", lambda x: self.resetTimer())

    def resetTimer(self):
        # establish global timer variable
        global timer

        c1.acquire()
        timer = TIMEOUT
        c1.release()

'''
    Battery Label Update Class
        Updates the label displaying power draw from the batter
            Inputs:
                chargingLbl - charging/not charging label to be updated
                powerLbl - power label to be updated
                timeLbl - charging time label to be updated
'''
class BatteryUpdateLabel(threading.Thread):
    def __init__(self, chargingLbl, powerLbl, timeLbl):
        threading.Thread.__init__(self)
        self.chargingLbl = chargingLbl
        self.powerLbl = powerLbl
        self.timeLbl = timeLbl

    def run(self):
        secondsCharging = 0

        while True:
            # read proportional current
            powerVal = adc.read_adc(BATTERY, gain=GAIN)

            print("Power Raw: " + str(powerVal))
            
            # cutoff value for battery not being drawn from
            CUTOFF = 1000

            if powerVal > CUTOFF:
                secondsCharging += 1
                # map input value to mA
                # TODO
                mAVal = powerVal
                mAhVal = mAVal * (secondsCharging / 3600)

                self.chargingLbl.config(text="Charging")
                self.powerLbl.config(text=str(round(mAhVal, 4))  + " mAh")
                self.timeLbl.config(text="Over " + str(secondsCharging)  + " seconds")
            else:
                self.chargingLbl.config(text="Not Charging")
                self.powerLbl.config(text="0 mAh")
                self.timeLbl.config(text="")
                secondsCharging = 0

            time.sleep(1)

# run the app
app = DisplayApp()
app.geometry("1024x768")
app.mainloop()
