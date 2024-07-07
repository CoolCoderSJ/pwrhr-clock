from machine import Pin,SPI,PWM
import framebuf
import time
import machine
import network

import asyncio
import _thread
from microdot import Microdot

app = Microdot()

@app.route('/')
async def index(request):
    return 'Hello, world!'

async def main():
    await app.start_server(port=80, debug=True)

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

   
if __name__=='__main__':
    LED = LED_8SEG()
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect("KidzBop", "9886341045")
    while not wifi.isconnected():
        pass
    print(wifi.ifconfig())

    t = _thread.start_new_thread(asyncio.run, (main(),))
    
    while 1:
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
