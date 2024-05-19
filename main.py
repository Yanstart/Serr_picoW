import time
import random
from machine import Pin, PWM
import utime
import network
import socket
import _thread

# Définition des pins pour le décodeur 74LS47
pin_a = Pin(1, Pin.OUT)
pin_b = Pin(2, Pin.OUT)
pin_c = Pin(4, Pin.OUT)
pin_d = Pin(5, Pin.OUT)

# Définition des pins pour les transistors des afficheurs 7 segments
transistor_units = Pin(19, Pin.OUT)
transistor_tens = Pin(20, Pin.OUT)

# Séquences pour chaque chiffre sur les 7 segments
digit_sequences = {
    0: (0, 0, 0, 0),
    1: (0, 0, 0, 1),
    2: (0, 0, 1, 0),
    3: (0, 0, 1, 1),
    4: (0, 1, 0, 0),
    5: (0, 1, 0, 1),
    6: (0, 1, 1, 0),
    7: (0, 1, 1, 1),
    8: (1, 0, 0, 0),
    9: (1, 0, 0, 1),
}

# Fonction pour se connecter au Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("Connected to WiFi")
    print(wlan.ifconfig())

# Fonction pour afficher un chiffre sur les 7 segments
def display_digit(digit):
    sequence = digit_sequences.get(digit, (0, 0, 0, 0))
    pin_a.value(sequence[0])
    pin_b.value(sequence[1])
    pin_c.value(sequence[2])
    pin_d.value(sequence[3])

# Fonction pour basculer entre les chiffres des unités et des dizaines
def toggle_digits():
    transistor_units.value(1)
    transistor_tens.value(0)
    utime.sleep_ms(5)
    transistor_units.value(0)
    transistor_tens.value(1)
    utime.sleep_ms(5)

# Classe pour l'affichage sur 7 segments
class Display:
    def __init__(self, pins, units_pin, tens_pin):
        self.pins = pins
        self.units_pin = units_pin
        self.tens_pin = tens_pin

    def display_temperature(self, temperature):
        tens = temperature // 10
        units = temperature % 10
        for _ in range(100):  # boucle pour maintenir l'affichage stable
            display_digit(tens)
            toggle_digits()
            display_digit(units)
            toggle_digits()

# Classe pour le contrôle du servo moteur
class ServoControl:
    def __init__(self, pin):
        self.servo = PWM(Pin(pin))
        self.servo.freq(50)

    def set_servo_angle(self, angle):
        duty_cycle = int(angle * (7803 - 1950) / 180) + 1950
        self.servo.duty_u16(duty_cycle)

    def control_servo(self, temperature):
        if temperature < 20:
            self.set_servo_angle(0)
            print("Porte fermée")
        elif temperature > 25:
            self.set_servo_angle(90)
            print("Porte ouverte")
        else:
            self.set_servo_angle(45)
            print("Porte entre-ouverte")

# Classe pour la lecture du capteur DHT11
class DHT11:
    def __init__(self, pin_name, display, servo_control):
        self.pin = Pin(pin_name)
        self.display = display
        self.servo_control = servo_control
        self.last_temperature = None

    def read_data(self):
        try:
            self.pin.init(Pin.OUT)
            self.pin.value(0)
            utime.sleep_ms(20)
            self.pin.value(1)
            self.pin.init(Pin.IN)
            utime.sleep_us(30)

            if self.pin.value() != 0:
                raise OSError

            data = []
            for _ in range(40):
                while self.pin.value() == 0:
                    pass
                k = 0
                while self.pin.value() == 1:
                    k += 1
                    if k > 100:
                        break
                data.append(0 if k < 3 else 1)

            humidity = int("".join(str(x) for x in data[0:8]), 2)
            temperature = int("".join(str(x) for x in data[16:24]), 2)

            if humidity + temperature != int("".join(str(x) for x in data[32:40]), 2):
                raise OSError

        except OSError:
            temperature = random.randint(0, 30)
            humidity = random.randint(40, 90)

        return temperature, humidity

    def update(self):
        temperature, humidity = self.read_data()
        print(f"Temperature: {temperature}C, Humidity: {humidity}%")

        if temperature != self.last_temperature:
            self.display.display_temperature(temperature)
            self.servo_control.control_servo(temperature)
            self.last_temperature = temperature

# Fonction pour la réponse HTML du serveur web
def html_response(temperature, humidity):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Serre Connectée</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; }}
            .button {{ padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Gestion de la Serre</h1>
        <p>Température: {temperature}C</p>
        <p>Humidité: {humidity}%</p>
        <button class="button" onclick="fetch('/open')">Ouvrir la porte</button>
        <button class="button" onclick="fetch('/close')">Fermer la porte</button>
    </body>
    </html>
    """
    return html

# Fonction principale pour le mode USB
def main_usb():
    display = Display([pin_a, pin_b, pin_c, pin_d], transistor_units, transistor_tens)
    servo_control = ServoControl(16)
    dht_sensor = DHT11(14, display, servo_control)

    print("Started")

    while True:
        dht_sensor.update()
        time.sleep(10)

# Fonction pour démarrer le serveur web
def web_server():
    display = Display([pin_a, pin_b, pin_c, pin_d], transistor_units, transistor_tens)
    servo_control = ServoControl(16)
    dht_sensor = DHT11(14, display, servo_control)

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Web server started on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)

        if '/open' in request:
            servo_control.set_servo_angle(90)
            print("Porte ouverte")
        elif '/close' in request:
            servo_control.set_servo_angle(0)
            print("Porte fermée")

        temperature, humidity = dht_sensor.read_data()
        print(f"Temperature: {temperature}C, Humidity: {humidity}%")

        dht_sensor.update()

        response = html_response(temperature, humidity)
        cl.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

# Fonction principale pour choisir le mode de connexion
def main():
    print("Select connection mode: 1 - USB, 2 - Wi-Fi")
    mode = input("Enter mode: ")

    if mode == "1":
        _thread.start_new_thread(main_usb, ())
    elif mode == "2":
        ssid = "YOUR_SSID"
        password = "YOUR_PASSWORD"
        connect_to_wifi(ssid, password)
        _thread.start_new_thread(web_server, ())
    else:
        print("Invalid mode selected")

if __name__ == "__main__":
    main()
