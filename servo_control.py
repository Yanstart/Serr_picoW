import time
import RPi.GPIO as GPIO

class ServoControl:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.servo = GPIO.PWM(self.pin, 50)  # Fréquence de 50 Hz pour le servo
        self.servo.start(0)

    def set_angle(self, angle):
        duty = angle / 18 + 2
        GPIO.output(self.pin, True)
        self.servo.ChangeDutyCycle(duty)
        time.sleep(1)
        GPIO.output(self.pin, False)
        self.servo.ChangeDutyCycle(0)

    def control_servo(self, temperature):
        seuil_temperature = 25
        if temperature > seuil_temperature:
            # Ouvrir la porte
            self.set_angle(90)
        else:
            # Fermer la porte
            self.set_angle(0)
