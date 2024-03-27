import time
import RPi.GPIO as GPIO
from flask import Flask, render_template
from dht11 import DHT11
from display import Display
from servo_control import ServoControl

# Initialisation de l'affichage
display = Display()

# Initialisation du contrôle du servo moteur
servo_pin = 16  # Broche GPIO pour le servo moteur
servo_control = ServoControl(servo_pin)

# Initialisation du capteur DHT11 avec prise en charge du servo moteur
dht_pin = 34  # Broche de données du capteur DHT11
dht_sensor = DHT11(dht_pin, display, servo_control)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/open')
def open_door():
    servo_control.set_angle(90)
    return 'Porte ouverte'

@app.route('/close')
def close_door():
    servo_control.set_angle(0)
    return 'Porte fermée'

def main():
    try:
        while True:
            # Lecture des données du capteur DHT11
            data = dht_sensor.read_data()
            if data is not None:
                temperature = int(data[0])
                humidity = int(data[1])
                print("Temperature:", temperature, "°C")
                print("Humidity:", humidity, "%")
            time.sleep(2)  # Attend 2 secondes avant la prochaine lecture

    except KeyboardInterrupt:
        print("Programme arrêté par l'utilisateur.")

    finally:
        GPIO.cleanup()  # Nettoyage des ports GPIO lors de l'arrêt du programme

if __name__ == '__main__':
    main()
