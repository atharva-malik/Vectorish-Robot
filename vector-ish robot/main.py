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

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf

WIDTH = 128
HEIGHT= 64

i2c = I2C(0, scl=Pin(17), sda = Pin(16), freq=200000) # 8, 9 are the default values

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

oled.fill(0) # CLEAR SCREEN
oled.text("Hello, World!", 0,0)
oled.show()
