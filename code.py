from machine import Pin,SPI,PWM
import framebuf
import time
import machine
import network
import urequests

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("KidzBop", "9886341045")
while not wifi.isconnected():
    pass
print(wifi.ifconfig())
    
import asyncio
import _thread
from microdot import Microdot

app = Microdot()

@app.route('/stopwatch')
async def index(request):
    global STOPW_T, MODE
    t = request.args.get("t")
    STOPW_T = int(t) + 1
    MODE = "STOPWATCH"
    return 'OK'

@app.route('/end_stop')
async def end_stop(request):
    global MODE
    MODE = "CLOCK"
    return "OK"

def main():
    app.run(port=80, debug=True)

def decrement(t):
    global STOPW_T, DOWN
    print("minus 1")
    STOPW_T -= 1
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
    global STOPW_T, MODE, DOWN, arcTime, arcDown
    print("Starting clock")
    while 1:
        print(MODE)
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
        elif MODE == "STOPWATCH":
            if STOPW_T > 0:
                timern = str(STOPW_T - 1)
                if len(timern) < 4:
                    timern = ((4-len(timern)) * "0") + timern
                
                LED.write_cmd(UNITS,LED.SEG8[int(timern[3])])
                LED.write_cmd(TENS,LED.SEG8[int(timern[2])])
                LED.write_cmd(HUNDREDS,LED.SEG8[int(timern[1])])
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
        
        elif MODE == "ARCADE":
            sessions = urequests.get("https://hackhour.hackclub.com/api/session/U03NJ5A39B7", headers={
            "Authorization": "Bearer -----"
            })
            print(sessions.status_code)
            sessions = sessions.json()
            if sessions['data']:
                sessMins = int(sessions['data']['endTime'].split("T")[1].split(":")[1])
                timern = time.localtime()
                minsLeft = sessMins - timern[4] - 1
                secsLeft = 60 - timern[5]
                minsLeft, secsLeft = str(minsLeft), str(secsLeft)
                if len(minsLeft) < 2: minsLeft = "0" + minsLeft
                if len(secsLeft) < 2: secsLeft = "0" + secsLeft
                
                arcTime = [int(minsLeft[0]), int(minsLeft[1]), int(secsLeft[0]), int(secsLeft[1])]
                timern = time.localtime()[5]
                while arcTime[0] > 0 and arcTime[1] > 0 and arcTime[2] > 0 and arcTime[3] > 0:
                    LED.write_cmd(UNITS, LED.SEG8(arcTime[3]))
                    LED.write_cmd(TENS, LED.SEG8(arcTime[2]))
                    LED.write_cmd(HUNDREDS, LED.SEG8(arcTime[1]))
                    LED.write_cmd(KILOBIT, LED.SEG8(arcTime[0]))
                    if not arcDown:
                            arcDown = True
                            tim = machine.Timer(-1)
                            tim.init(mode=machine.Timer.ONE_SHOT, period=1000, callback=arcDec)

arcTime = [0, 0, 0, 0]
arcDown = False
def decArc():
    if arcTime[2] == 0 and arcTime[3] == 0 and arcTime[0] + arcTime[1] > 0:
        if arcTime[1] == 0:
            arcTime[0] -= 1
            arcTime[1] = 9
        else:
            arcTime[1] -= 1
    
    elif sum(arcTime) > 0:
        if arcTime[3] == 0 and arcTime[2] > 0:
            arcTime[2] -= 1
            arcTime[3] = 9
            
        elif arcTime[3] > 0:
            arcTime[3] -= 1
            
    arcDown = False
        

if __name__=='__main__':
    sessions = urequests.get("https://hackhour.hackclub.com/api/session/U03NJ5A39B7", headers={
        'authorization': 'Bearer -----'
    })
    print(sessions.status_code)
    sessions = sessions.json()
        
    global MODE, STOPW_T, DOWN
    MODE = "ARCADE"
    STOPW_T = 0
    DOWN = False
    t = _thread.start_new_thread(u_clock, ())
    main()
