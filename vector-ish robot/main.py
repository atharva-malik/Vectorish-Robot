# DHT22: Combo temp and humidity sensor
# DS18B20: Temp sensor
# SSD1306: OLED Screen
# LED-BAR-GRAPH: Led bar graph
# Buzzer: Buzzer
# MPU6050: Accelerometer
# PinOut: https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg
# https://codepen.io/KjeldSchmidt/pen/KaRPzX

# Animation Imports
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf, time, random
from animations import *
import accel

# Time Imports
import network
import urequests

# Temp imports
from dht import DHT22

tempSensor = DHT22(4)

# TIME
# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Fill in your network name (ssid) and password here:
ssid = ''
password = ''
# wlan.connect(ssid, password)

# Animation setup
STATE = "a" # A for awake, S for asleep FIX THIS WHEN YOU SUBMIT IT
WIDTH = 128
HEIGHT= 64
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000) # 8, 9 are the default values
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Accelerometer Setup
i2c2 = I2C(1, sda=Pin(10), scl=Pin(11))

# Gonna keep this for debugging
year = 2024
month = 8
date = 7
hour = 7
minute = 59
second = 30

# SLEEP_MINUTE = random.randint(0,30)
# WAKE_MINUTE = random.randint(0,30)
# JUST FOR TESTING
SLEEP_MINUTE = 0
WAKE_MINUTE = 0

# Helper Functions
def getTime(testing=False):
    if not testing:
        url = "https://timeapi.io/api/Time/current/zone?timeZone=Australia/ACT"
        r = urequests.get("http://www.google.com").json()
        year = r["year"]
        month = r["month"]
        date = r["day"]
        hour = r["hour"]
        minute = r["minute"]
        second = r["seconds"]
    else:
        year = 2024
        month = 8
        date = 7
        hour = 7
        minute = 59
        second = 30
    return year, month, date, hour, minute, second

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

def checkPickupFall():
    gs = accel.mpu6050_get_accel(i2c2)
    rot = accel.mpu6050_get_gyro(i2c2)
    xg = gs[0]
    yg = gs[1]
    zg = gs[2]
    xrot = rot[0]
    yrot = rot[1]
    zrot = rot[2]
    if zg > 1: # Sudden pick up
        return "panic"
    elif xg > 1 or yg > 1: # Sudden shake
        return "shake"
    elif zrot > 0.5 or zrot < 0.5: # Fallen down
        return "panic"
    else:
        return "NA"

# State functions
def awake(temp, humidity):
    displayImage(EYES, 64, 64)
    if random.randint(0, 100) > 80: # This number works quite well
        displayAnimation(BLINK, 64, 64)
    elif random.randint(0, 100) > 95: # Checking for cold
        if temp < 15:
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

def panic():
    displayAnimation(SHIVERING, 64, 64) # The same animation will work

def managePickupFall():
    stage = checkPickupFall()
    if stage == "NA": # This is first cuz this is gonna be the case most of the time
        return
    elif stage == "panic":
        panic()
    elif stage == "shake":
        dizzy()

oled.fill(0) # CLEAR SCREEN
accel.mpu6050_init(i2c2)
awake_transition()
while True:
    print("Accelerometer:\t", accel.mpu6050_get_accel(i2c2), "g") #Print Accelerometer values (X,Y,Z) 
    print("Gyroscope:\t", accel.mpu6050_get_gyro(i2c2), "°/s") #Print Gyroscope values (X,Y,Z)
    temp, humidity = getTemp()
    year, month, date, hour, minute, second = getTime(True)
    if hour >= 22 and minute >= SLEEP_MINUTE: # Sleep!
        if STATE == "a": # Just slept
            sleep_transition()
            WAKE_MINUTE = random.randint(0,30)
            STATE = "s"
        sleep()
    elif hour >= 7 and minute >= WAKE_MINUTE: # Awake!
        if STATE == "s": # Just woke up
            awake_transition()
            SLEEP_MINUTE = random.randint(0,30)
            state = "a"
        awake(temp, humidity)
    else:
        sleep() # Edge case
        STATE = "s"
    
    managePickupFall()
