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
from dht import DHT22
from urtc import DS1307
import utime

tempSensor = DHT22(4)

# Animation setup
STATE = "a" # A for awake, S for asleep FIX THIS WHEN YOU SUBMIT IT
WIDTH = 128
HEIGHT= 64
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=200000) # 8, 9 are the default values
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Time setup
i2c1 = I2C(1,scl=Pin(3),sda=Pin(2))
rtc = DS1307(i2c1)

# Accelerometer Setup
p16 = Pin(16, Pin.OUT)
i2c2 = I2C(1, sda=Pin(10), scl=Pin(11))
p16.value(1)

# Gonna keep this for debugging
year = 2024
month = 8
date = 7
day = 3
hour = 7
minute = 59
second = 30

now = (year,month,date,day,hour,minute,second,0)
# rtc.datetime(now)

# SLEEP_MINUTE = random.randint(0,30)
# WAKE_MINUTE = random.randint(0,30)
# JUST FOR TESTING
SLEEP_MINUTE = 0
WAKE_MINUTE = 0


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

oled.fill(0) # CLEAR SCREEN
accel.mpu6050_init(i2c2)
awake_transition()
while True:
    print("Accelerometer:\t", accel.mpu6050_get_accel(i2c2), "g") #Print Accelerometer values (X,Y,Z) 
    print("Gyroscope:\t", accel.mpu6050_get_gyro(i2c2), "°/s") #Print Gyroscope values (X,Y,Z)
    temp, humidity = getTemp()
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()

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
        sleep() # Outside case
        STATE = "s"
