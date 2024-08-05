// DHT22: Combo temp and humidity sensor
// DS18B20: Temp sensor
// SSD1306: OLED Screen
// LED-BAR-GRAPH: Led bar graph
// Buzzer: Buzzer
// MPU6050: Accelerometer
// PinOut: https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg

// First I want to get the screen working: https://wokwi.com/projects/344894074741850707
// Something like a default animation: https://animator.wokwi.com/
// https://codepen.io/KjeldSchmidt/pen/KaRPzX

void setup() {
  // put your setup code here, to run once:
  Serial1.begin(115200);
  Serial1.println("Hello, Raspberry Pi Pico W!");
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1); // this speeds up the simulation
}
