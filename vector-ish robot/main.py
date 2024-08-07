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

# Time Imports
import utime
from urtc import DS1307

# Temp Imports
from dht import DHT22

tempSensor = DHT22(2)

# Animation setup
STATE = "a" # A for awake, S for asleep
WIDTH = 128
HEIGHT= 64
i2c = I2C(0, scl=Pin(17), sda = Pin(16), freq=200000) # 8, 9 are the default values
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Time setup

# wintertime / Summertime
GMT_OFFSET = 3600 * 1 # 3600 = 1 h (wintertime)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (summertime)



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

def getTemp():
    try:
        tempSensor.measure()
        temp = tempSensor.temperature()
        humidity = tempSensor.humidity()
    except Exception as e:
        print("Toundi", e)
        temp, humidity = -1
    return temp, humidity

# State functions
def awake(temp, humidity):
    displayImage(EYES, 64, 64)
    if random.randint(0, 100) > 80: # This number works quite well
        displayAnimation(BLINK, 64, 64)
    elif random.randint(0, 100) > 95: # Checking for cold
        if temp < 13:
            for i in range(15):
                displayAnimation(SHIVERING, 64, 64)
    
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
    temp, humidity = getTemp()
    if STATE == "a": #TODO: Make this more advanced using api keys
        awake(temp, humidity)
        if random.randint(1,1000) > 999: # Since this runs really fast this value is good
            STATE = "s"
            sleep_transition()
    if STATE == "s":
        sleep()
        if random.randint(1,1000) > 999: # I also just did a lot of trial and error and found this works best
            STATE = "a"
            awake_transition()
    oled.text("Hello, World!", 0,0)
