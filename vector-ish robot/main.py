# DHT22: Combo temp and humidity sensor
# DS18B20: Temp sensor
# SSD1306: OLED Screen
# LED-BAR-GRAPH: Led bar graph
# Buzzer: Buzzer
# MPU6050: Accelerometer
# PinOut: https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg

# First I want to get the screen working: https://wokwi.com/projects/344894074741850707
# Something like a default animation: https://animator.wokwi.com/
# https://codepen.io/KjeldSchmidt/pen/KaRPzX

# Animation Imports
from machine import Pin, I2C, RTC
from ssd1306 import SSD1306_I2C
import framebuf, time, random
from animations import *
from statics import *

# Time Imports
import rp2, sys, network
import utime as time
import usocket as socket
import ustruct as struct

# Animation setup
STATE = "a" # A for awake, S for asleep
WIDTH = 128
HEIGHT= 64
i2c = I2C(0, scl=Pin(17), sda = Pin(16), freq=200000) # 8, 9 are the default values
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Time setup
ssid = "ENTER-HERE"
password = "ENTER-HERE"

# wintertime / Summertime
GMT_OFFSET = 3600 * 1 # 3600 = 1 h (wintertime)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (summertime)

# NTP-Host
NTP_HOST = 'pool.ntp.org'

# Function: get time from NTP Server
def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)

# Function: copy time to PI pico's RTC
def setTimeRTC():
    tm = getTimeNTP()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    

  
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
    
max_wait = 10
print('Waiting for connection')
while max_wait > 10:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1    
    sleep(1)
status = None
if wlan.status() != 3:
    raise RuntimeError('Connections failed')
else:
    status = wlan.ifconfig()
    print('connection to', ssid,'succesfull established!', sep=' ')
    print('IP-adress: ' + status[0])
ipAddress = status[0]
rtc = RTC()
# Set time
setTimeRTC()


# Helper functions
def displayImage(img, sizeX, sizeY):
    oled.fill(0)
    fb = framebuf.FrameBuffer(img, sizeX, sizeY, framebuf.MONO_HLSB) # This means monochrome
    oled.blit(fb, int((WIDTH-sizeX)/2), 0)
    oled.show()

def displayAnimation(stages, sizeX, sizeY, speed=0.01):
    for i in stages:
        time.sleep(speed)
        displayImage(i, sizeX, sizeY)


# State functions
def awake():
    displayImage(EYES, 64, 64)
    time.sleep(random.randint(1, 3))
    displayAnimation(BLINK, 64, 64)
    
def sleep_transition():
    time.sleep(0.5)
    displayImage(SWITCH_TO_SLEEP[0], 64, 64)
    time.sleep(0.5)
    displayImage(SWITCH_TO_SLEEP[1], 64, 64)
    time.sleep(0.2)
    displayImage(SWITCH_TO_SLEEP[2], 64, 64)
    time.sleep(0.1)
    displayImage(SWITCH_TO_SLEEP[3], 64, 64)
    time.sleep(0.3)
    displayImage(SWITCH_TO_SLEEP[4], 64, 64)

def awake_transition():
    time.sleep(0.5)
    displayImage(SWITCH_TO_SLEEP[4], 64, 64)
    time.sleep(0.5)
    displayImage(SWITCH_TO_SLEEP[3], 64, 64)
    time.sleep(0.2)
    displayImage(SWITCH_TO_SLEEP[2], 64, 64)
    time.sleep(0.1)
    displayImage(SWITCH_TO_SLEEP[1], 64, 64)
    time.sleep(0.3)
    displayImage(SWITCH_TO_SLEEP[0], 64, 64)

def sleep():
    displayAnimation(SLEEP, 64, 64, 0.3)

oled.fill(0) # CLEAR SCREEN
awake_transition()
while True:
    if STATE == "a": #TODO: Make this more advanced using api keys
        awake()
        if random.randint(1,100) > 95: # Since this runs really fast this value is good
            STATE = "s"
            sleep_transition()
    if STATE == "s":
        sleep()
        if random.randint(1,100) > 95: # I also just did a lot of trial and error and found this works best
            STATE = "a"
            awake_transition()
    # oled.text("Hello, World!", 0,0)
