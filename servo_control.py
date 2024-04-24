from machine import Pin, Timer, ADC, PWM
import utime
import time

servoPin = Pin(16)
servo = PWM(servoPin)
duty_cycle = 0
servo.freq(50)  
def setservo(angle):
    duty_cycle = int(angle*(7803-1950)/180) + 1950
    servo.duty_u16(duty_cycle)
setservo(90)
while 1:
    setservo(0)
    time.sleep(1)
    setservo(180)
    time.sleep(1)
    setservo(0)

