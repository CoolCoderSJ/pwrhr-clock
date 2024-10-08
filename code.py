from machine import Pin,SPI,PWM
import framebuf
import time
import machine
import network
import requests
import gc

wifi = network.WLAN(network.STA_IF)
wifi.config(pm = 0x111022)
wifi.active(True)
wifi.connect("KidzBop", "--------------")
while not wifi.isconnected():
    pass
print(wifi.ifconfig())
    
import asyncio
import _thread
import socket

def decrement(t):
    global TIMER_T, DOWN, timerPaused
    print("minus 1")
    if not timerPaused: TIMER_T -= 1
    DOWN = False

MOSI = 11
SCK = 10    
RCLK = 9

KILOBIT   = 0xFE
HUNDREDS  = 0xFD
TENS      = 0xFB
UNITS     = 0xF7
Dot       = 0x80

SEG8Code = [
    0x3F, # 0
    0x06, # 1
    0x5B, # 2
    0x4F, # 3
    0x66, # 4
    0x6D, # 5
    0x7D, # 6
    0x07, # 7
    0x7F, # 8
    0x6F, # 9
    0x77, # A
    0x7C, # b
    0x39, # C
    0x5E, # d
    0x79, # E
    0x71  # F
    ] 
class LED_8SEG():
    def __init__(self):
        self.rclk = Pin(RCLK,Pin.OUT)
        self.rclk(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.SEG8=SEG8Code
    '''
    function: Send Command
    parameter: 
        Num: bit select
        Seg：segment select       
    Info:The data transfer
    '''
    def write_cmd(self, Num, Seg):    
        self.rclk(1)
        self.spi.write(bytearray([Num]))
        self.spi.write(bytearray([Seg]))
        self.rclk(0)
        time.sleep(0.002)
        self.rclk(1)


LED = LED_8SEG()

def u_clock():
    global TIMER_T, MODE, DOWN, STOPW_T, arcTime, arcDown, stopPaused, lasttick
    print("Starting clock")
    while 1:
        gc.collect()
        
        if MODE == "CLOCK":
            rn = time.localtime()
            mins = str(rn[4])
            hr = str(rn[3])
            if int(hr) > 12: hr = str(int(hr)-12)
            min1, min2, hr1, hr2 = 0, 0, 0, 0

            if len(mins) == 1:
                min1 = 0
                min2 = int(mins)
            else:
                min1 = int(mins[0])
                min2 = int(mins[1])
            
            if len(hr) == 1:
                hr1 = 0
                hr2 = int(hr)
            else:
                hr1 = int(hr[0])
                hr2 = int(hr[1])
                
            LED.write_cmd(UNITS,LED.SEG8[min2])
            LED.write_cmd(TENS,LED.SEG8[min1])
            LED.write_cmd(HUNDREDS,LED.SEG8[hr2]|Dot)
            LED.write_cmd(KILOBIT,LED.SEG8[hr1])
        elif MODE == "TIMER":
            if TIMER_T > 0:
                rn = TIMER_T - 1
                mins = str(rn // 60)
                secs = str(rn - int(mins) * 60)
                
                if len(mins) < 2: mins = "0" + mins
                if len(secs) < 2: secs = "0" + secs
                
                timern = f"{mins}{secs}"
                
                if not timerPaused:
                    LED.write_cmd(UNITS,LED.SEG8[int(timern[3])])
                    LED.write_cmd(TENS,LED.SEG8[int(timern[2])])
                    LED.write_cmd(HUNDREDS,LED.SEG8[int(timern[1])]|Dot)
                    LED.write_cmd(KILOBIT,LED.SEG8[int(timern[0])])
                else:
                    LED.write_cmd(UNITS,0x00)
                    LED.write_cmd(TENS,0x00)
                    LED.write_cmd(HUNDREDS,0x00)
                    LED.write_cmd(KILOBIT,0x00)
                    time.sleep(1)
                    rnTicks = time.ticks_ms()
                    while time.ticks_diff(time.ticks_ms(), rnTicks) < 1000:
                        LED.write_cmd(UNITS,LED.SEG8[int(timern[3])])
                        LED.write_cmd(TENS,LED.SEG8[int(timern[2])])
                        LED.write_cmd(HUNDREDS,LED.SEG8[int(timern[1])]|Dot)
                        LED.write_cmd(KILOBIT,LED.SEG8[int(timern[0])])
                
                if not DOWN:
                    DOWN = True
                    tim = machine.Timer(-1)
                    tim.init(mode=machine.Timer.ONE_SHOT, period=1000, callback=decrement)
            else:
                LED.write_cmd(UNITS,0x00)
                LED.write_cmd(TENS,0x00)
                LED.write_cmd(HUNDREDS,0x00)
                LED.write_cmd(KILOBIT,0x00)
                time.sleep(1)
                timern = time.localtime()[5]
                while time.localtime()[5] - timern < 1:
                    LED.write_cmd(UNITS,0x3F)
                    LED.write_cmd(TENS,0x3F)
                    LED.write_cmd(HUNDREDS,0x3F)
                    LED.write_cmd(KILOBIT,0x3F)
        
        elif MODE == "STOPWATCH":
            if not lasttick:
                lasttick = time.ticks_ms()
            
            if time.ticks_diff(time.ticks_ms(), lasttick) >= 1000:
                if not stopPaused: STOPW_T += 1
                lasttick = time.ticks_ms()
            
            mins = str(STOPW_T // 60)
            secs = str(STOPW_T - int(mins)*60)
            if len(mins) < 2: mins = "0" + mins
            if len(secs) < 2: secs = "0" + secs
            stopStr = f"{mins}{secs}"
            
            if not stopPaused:
                LED.write_cmd(UNITS,LED.SEG8[int(stopStr[3])])
                LED.write_cmd(TENS,LED.SEG8[int(stopStr[2])])
                LED.write_cmd(HUNDREDS,LED.SEG8[int(stopStr[1])]|Dot)
                LED.write_cmd(KILOBIT,LED.SEG8[int(stopStr[0])])
            else:
                LED.write_cmd(UNITS,0x00)
                LED.write_cmd(TENS,0x00)
                LED.write_cmd(HUNDREDS,0x00)
                LED.write_cmd(KILOBIT,0x00)
                time.sleep(1)
                timern = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), timern) < 1000:
                    LED.write_cmd(UNITS,LED.SEG8[int(stopStr[3])])
                    LED.write_cmd(TENS,LED.SEG8[int(stopStr[2])])
                    LED.write_cmd(HUNDREDS,LED.SEG8[int(stopStr[1])]|Dot)
                    LED.write_cmd(KILOBIT,LED.SEG8[int(stopStr[0])])    
                
        elif MODE == "ARCADE":
            global sessions
            if sessions['data']:
                if sum(arcTime) == 0:
                    sessMins = int(sessions['data']['endTime'].split("T")[1].split(":")[1])
                    timern = time.localtime()
                    minsLeft = sessMins - timern[4] - 1
                    if minsLeft < 0: minsLeft += 60
                    secsLeft = 60 - timern[5]
                    minsLeft, secsLeft = str(minsLeft), str(secsLeft)
                    if len(minsLeft) < 2: minsLeft = "0" + minsLeft
                    if len(secsLeft) < 2: secsLeft = "0" + secsLeft
                    
                    #print(minsLeft, secsLeft, sessMins)
                    
                    arcTime = [int(minsLeft[0]), int(minsLeft[1]), int(secsLeft[0]), int(secsLeft[1])]

                while sum(arcTime) > 0 and MODE == "ARCADE":
                    LED.write_cmd(UNITS, LED.SEG8[arcTime[3]])
                    LED.write_cmd(TENS, LED.SEG8[arcTime[2]])
                    LED.write_cmd(HUNDREDS, LED.SEG8[arcTime[1]]|Dot)
                    LED.write_cmd(KILOBIT, LED.SEG8[arcTime[0]])
                    if not arcDown:
                        #print("starting timer")
                        arcDown = True
                        tim = machine.Timer(-1)
                        tim.init(mode=machine.Timer.ONE_SHOT, period=1000, callback=arcDec)
                
                while MODE == "ARCADE":
                    LED.write_cmd(UNITS,0x00)
                    LED.write_cmd(TENS,0x00)
                    LED.write_cmd(HUNDREDS,0x00)
                    LED.write_cmd(KILOBIT,0x00)
                    time.sleep(1)
                    timern = time.localtime()[5]
                    while time.localtime()[5] - timern < 1:
                        LED.write_cmd(UNITS,0x3F)
                        LED.write_cmd(TENS,0x3F)
                        LED.write_cmd(HUNDREDS,0x3F)
                        LED.write_cmd(KILOBIT,0x3F)
                        


arcTime = [0, 0, 0, 0]


def arcDec(t):
    global arcDown, arcTime, paused, sessions
    #print("arcDec callback")
    
    if not paused:
        if arcTime[2] == 0 and arcTime[3] == 0 and arcTime[0] + arcTime[1] == 1:
            if arcTime[1] == 0:
                arcTime[0] -= 1
                arcTime[1] = 9
            else:
                arcTime[1] -= 1
        
        elif arcTime[2] + arcTime[3] == 0 and arcTime[0] + arcTime[1] > 1:
            if arcTime[1] > 0:
                arcTime[1] -= 1
                arcTime[2] = 5
                arcTime[3] = 9
                
            elif arcTime[0] > 0 and arcTime[1] == 0:
                arcTime[0] -= 1
                arcTime[1] = 9
                arcTime[2] = 5
                arcTime[3] = 9
        
        elif sum(arcTime) > 0:
            if arcTime[3] == 0 and arcTime[2] > 0:
                arcTime[2] -= 1
                arcTime[3] = 9
                
            elif arcTime[3] > 0:
                arcTime[3] -= 1
        
        #print("ARCTIME", arcTime)
         
    arcDown = False
        

if __name__=='__main__':
    MODE = "CLOCK"
    TIMER_T = 0
    STOPW_T = 0
    DOWN = False
    sessions = None
    arcDown = False
    paused = False
    lastTen = None
    lasttick = None
    stopPaused = False
    timerPaused = False
    
    t = _thread.start_new_thread(u_clock, ())

    
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen()
    s.settimeout(5)
    
    print('Listening on', addr)

    while True:
        gc.collect()
        
        if not lastTen:
            lastTen = time.ticks_ms()
        if time.ticks_diff(time.ticks_ms(), lastTen) > 10000:
            print("GETTING DATA")
            if MODE == "ARCADE":
                sr = requests.get("https://hackhour.hackclub.com/api/session/U03NJ5A39B7", headers={
                    'authorization': 'Bearer -----------'
                })
                sessions = sr.json()
                sr.close()
                print(sessions)
                
                if sessions['data']['paused']:
                    paused = True
                else:
                    sesStr = str(sessions['data']['remaining'])
                    if len(sesStr) < 2: sesStr = "0" + sesStr
                    arcTime = [int(sesStr[0]), int(sesStr[1]), 0, 0]
                    paused = False
                    
            lastTen = time.ticks_ms()
        else:
            print(time.ticks_diff(time.ticks_ms(), lastTen))
        
        try:
            conn, addr = s.accept()
            print('Got a connection from', addr)
            
            # Receive and parse the request
            request = conn.recv(1024)
            request = str(request)
            print('Request content = %s' % request)

            try:
                request = request.split()[1]
                print('Request:', request)
            except IndexError:
                pass
            
            path = request.split("?")[0]
            args = request.split("?")[1] if "?" in request else ""
            
            if path == '/timer':
                t = args.split("=")[1]
                TIMER_T = int(t) + 1
                timerPaused = False
                MODE = "TIMER"
            
            if path == "/clock":
                MODE = "CLOCK"
            
            if path == "/stopwatch":
                STOPW_T = 0
                stopPaused = False
                MODE = "STOPWATCH"
            
            if path == "/stopwatch/pause":
                stopPaused = True
            
            if path == "/stopwatch/unpause":
                stopPaused = False
                
            if path == "/timer/pause":
                timerPaused = True
            
            if path == "/timer/unpause":
                timerPaused = False
            
            if path == "/arcade":
                sr = requests.get("https://hackhour.hackclub.com/api/session/U03NJ5A39B7", headers={
                    'authorization': 'Bearer -----------'
                })
                sessions = sr.json()
                sr.close()
                print(sessions)
                MODE = "ARCADE"
            
            # Send the HTTP response and close the connection
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
            conn.close()

        except OSError as e:
            if e.args[0] == 110: # Timeout error code
                print('Timeout occurred')
            try: conn.close()
            except NameError: pass
            print('Connection closed')

