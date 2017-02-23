import tkinter as tk
from tkinter import ttk
import time
import random
import threading

LARGE_FONT = ("Verdana", "12")

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
        title = ttk.Label(self, text = "Lake Metroparks Farmpark Solar Tracker", font = LARGE_FONT)
        title.grid(row=0, column=1, sticky="N")

        test = ttk.Label(self, text = "0", font = LARGE_FONT)
        test.grid(row=1, column=1, sticky="N")

        # update I/O values
        t = IOUpdate(test, 0.5)
        t.daemon = True
        t.start()

        audioBtn = ttk.Button(self, text = "Audio Experiments", command = lambda: controller.show_frame(AudioPage))
        audioBtn.config(width=40)
        audioBtn.grid(row = 2, column=0, sticky="W", padx=20, pady=40)
        batteryBtn = ttk.Button(self, text = "Battery Diagnostics", command = lambda: controller.show_frame(BatteryPage))
        batteryBtn.config(width=40)
        batteryBtn.grid(row=2, column=2, sticky="E", padx=40, pady=40)

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
        title = ttk.Label(self, text = "Audio Experiments", font = LARGE_FONT)
        title.pack(pady = 10, padx = 10)

        landingBtn = ttk.Button(self, text = "Back to Landing", command = lambda: controller.show_frame(LandingPage))
        landingBtn.pack()

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
