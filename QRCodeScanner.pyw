#benötigte Module werden importiert
import tkinter
from cv2 import cvtColor, COLOR_BGR2RGB, VideoCapture
import PIL.Image, PIL.ImageTk
import time
import pyzbar.pyzbar as pyzbar
import simpleaudio
import pyperclip
import pyautogui as pya
import webbrowser
import keyboard

#start
class App:
    def __init__(self, window, window_title):
        
        #tkinter UI Vorbereitungen
        self.window = window
        self.window.title(window_title)
        self.window.iconbitmap("favicon.ico")
        
        #Videoquelle wird auf 0 gesetzt
        self.changeVideoInput(0)
                
        #UI: Canvas für das Video wird erstellt
        self.canvas = tkinter.Canvas(window, width = self.camera.get(3), height = self.camera.get(4))
        self.canvas.pack()
        
        #UI: Gescannten Code anzeigen
        frame0 = tkinter.Frame(window)
        frame0.pack()
        self.inputCode = tkinter.Entry(frame0, width=35, font = "Helvetica 15", justify="center")
        self.inputCode.pack(side="left")
        self.buttonCode = tkinter.Button(frame0, text="öffnen", command=lambda:self.openWebsite(self.inputCode.get()))
        self.buttonCode.pack(side="left", padx=6)
        
        #UI: Modus auswählen
        self.scanModus = "auto"
        self.tempScanMode = "manuell"
        self.radioGroup = tkinter.StringVar(self.window, "auto")
        frameModus = tkinter.Frame(window)
        frameModus.pack()
        self.labelRadio = tkinter.Label(frameModus, text="Scanntyp:")
        self.labelRadio.pack(side="left")
        self.radioModus1 = tkinter.Radiobutton(frameModus, text="auto", variable=self.radioGroup, value="auto", command=lambda:self.changeScanMode())
        self.radioModus1.pack(side="left")
        self.radioModus2 = tkinter.Radiobutton(frameModus, text="manuell", variable=self.radioGroup, value="manuell", command=lambda:self.changeScanMode())
        self.radioModus2.pack(side="left")
        self.buttonRadio = tkinter.Button(frameModus, text="scan (ESC)", command=lambda:self.changeTempScanMode())
        self.buttonRadio.pack(side="left", padx=6)
                
        #UI: Kamera auswählen
        frame1 = tkinter.Frame(window)
        frame1.pack()
        self.labelCamera = tkinter.Label(frame1, text="Kamera wählen (0-n):")
        self.labelCamera.pack(side="left")
        self.inputCamera = tkinter.Entry(frame1)
        self.inputCamera.pack(side="left")
        self.set_text(self.inputCamera, "0")
        self.buttonCamera = tkinter.Button(frame1, text="ok", command=lambda:self.changeVideoInput(int(self.inputCamera.get())))
        self.buttonCamera.pack(side="left", padx=6)

        #UI: Aktion nach Scann auswählen
        self.actions = ["enter"]
        frame2 = tkinter.Frame(window)
        frame2.pack()
        self.labelAction = tkinter.Label(frame2, text="Aktion nach Scannen wählen:")
        self.labelAction.pack(side="left")
        self.inputAction = tkinter.Entry(frame2)
        self.inputAction.pack(side="left")
        self.set_text(self.inputAction, "enter")
        self.buttonAction = tkinter.Button(frame2, text="ok", command=lambda:self.changeActions())
        self.buttonAction.pack(side="left", padx=6)

        #UI: Informationen Link
        frame4 = tkinter.Frame(window)
        frame4.pack()
        linkInfo = tkinter.Label(frame4, text="weitere Informationen", fg="blue", cursor="hand2")
        linkInfo.pack()
        linkInfo.bind("<Button-1>", lambda e: self.openWebsite("https://unsere-schule.org/programmieren/python/programme/qr-code-scanner-programmieren/"))
        
        #Delay einfügen, wie oft das Video aktualisiert werden soll
        self.delay = 15
        self.update()
        
        #wenn man im manuellen Scanmodus ist, wird mit der Taste ESC gescannt
        keyboard.add_hotkey("esc", lambda:self.changeTempScanMode())
        
        self.window.wm_attributes("-topmost", 1)
        self.window.mainloop()

    #Scanmode wird temporär geändert
    def changeTempScanMode(self):
        self.tempScanMode = "auto"
    
    #Scanmode wird dauerhaft geändert
    def changeScanMode(self):
        if(self.radioGroup.get() == "auto"):
            self.scanModus = "auto"
        else:
            self.scanModus = "manuell"
        
    #öffnet den Browser mit der übergebenen URL
    def openWebsite(self, url):
        webbrowser.open_new(url)
   
    #erstellt aus einem String ein Array für die Aktionen, die nach dem Scann ausgeführt werden sollen
    def changeActions(self):
        self.actions = self.inputAction.get().replace(" ", "").split(",")
        self.window.focus()
        
    #verändert die Quelle der Webcam
    def changeVideoInput(self, videoSource):
        self.camera = VideoCapture(videoSource)
        self.window.focus()
    
    #fügt Text in ein Textfeld ein 
    def set_text(self, tempEntry, text):
        tempEntry.delete(0,tkinter.END)
        tempEntry.insert(0,text)
        return
    
    #spielt ein Geräusch nach dem Scannen
    def playBeep(self):
        filename = 'beep.wav'
        wave_obj = simpleaudio.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        
    #aktualisiert das Kamerabild
    def update(self):
           
        #holt das aktuelle Bild der Kamera
        ret, frame = self.camera.read()        
        if ret:
            if(self.scanModus == "auto" or self.tempScanMode == "auto"):
                frame, found = self.read_barcodes(frame)
            else:
                found = 0
            frame = cvtColor(frame, COLOR_BGR2RGB)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            #wurde ein Code gefunden
            if(found == 1):                
                time.sleep(1)
                if(self.tempScanMode == "auto"):
                    self.tempScanMode = "manuell"
                
        self.window.after(self.delay, self.update)

    #es wird nach einem QR-Code bzw. Barcode gesucht
    def read_barcodes(self, frame):
        barcodes = pyzbar.decode(frame)       
        for barcode in barcodes:
            barcode_info = barcode.data.decode('utf-8')
            #Code wird in die Zwischenablage kopiert und eingefügt
            pyperclip.copy(barcode_info)
            #strg + v - also das Einfügen des Inhalts aus der Zwischenablage wird simuliert
            pya.keyDown('ctrl')
            pya.keyDown('v')
            pya.keyUp('ctrl')
            pya.keyUp('v')
            self.playBeep()
            time.sleep(0.1)
            #weitere Aktion wird ausgeführt
            for action in self.actions:
                pya.hotkey(action)
                time.sleep(0.1)
                           
            self.set_text(self.inputCode, barcode_info)
            return frame, 1
        return frame, 0


#Ein Objekt der Klasse App wird erstellt
App(tkinter.Tk(), "QRCodeScanner")