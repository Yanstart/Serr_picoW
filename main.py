import usocket as socket
import utime
import network
from machine import Pin, PWM

class DHT11:
    def __init__(self, pin_name):
        utime.sleep_ms(1000)
        self.N1 = Pin(pin_name, Pin.OUT)
        self.PinName = pin_name
        utime.sleep_ms(10)

    def read_data(self):
        self.__init__(self.PinName)
        data = []
        j = 0
        N1 = self.N1
        N1.low()
        utime.sleep_ms(20)
        N1.high()
        N1 = Pin(self.PinName, Pin.IN)
        utime.sleep_us(30)
        if N1.value() != 0:
            return [0, 0]
        while N1.value() == 0:
            continue
        while N1.value() == 1:
            continue
        while j < 40:
            k = 0
            while N1.value() == 0:
                continue
            while N1.value() == 1:
                k += 1
                if k > 100:
                    break
            if k < 3:
                data.append(0)
            else:
                data.append(1)
            j = j + 1
        print('DHT11 running')
        j = 0
        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        check_bit = data[32:40]
        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0
        for i in range(8):
            humidity += humidity_bit[i] * 2 ** (7 - i)
            humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
            temperature += temperature_bit[i] * 2 ** (7 - i)
            temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
            check += check_bit[i] * 2 ** (7 - i)
        tmp = humidity + humidity_point + temperature + temperature_point
        if check == tmp:
            print('Temperature:', temperature, '°C - Humidity:', humidity, '%')
        else:
            print('Error:', humidity, humidity_point, temperature, temperature_point, check)
        return [temperature, humidity]

# Définition des broches du Raspberry Pi Pico
servoPin = Pin(16)
transistor_units = Pin(19, Pin.OUT)
transistor_tens = Pin(20, Pin.OUT)
dht = DHT11(28)

# Configuration du servomoteur
servo = PWM(servoPin)
duty_cycle = 0
servo.freq(50)

# Seuils pour ouvrir et fermer la porte de la serre
TEMPERATURE_THRESHOLD = 30  # Seuil de température en degrés Celsius
HUMIDITY_THRESHOLD = 70  # Seuil d'humidité en pourcentage

# Fonction pour afficher un chiffre sur les 7 segments
def display_digit(digit):
    sequence = digit_sequences.get(digit, (0, 0, 0, 0))
    transistor_units.value(sequence[0])
    transistor_tens.value(sequence[1])
    # Insérer les valeurs des autres broches ici

# Fonction pour basculer entre les chiffres des unités et des dizaines
def toggle_digits():
    transistor_units.value(1)
    transistor_tens.value(0)
    utime.sleep_ms(5)
    transistor_units.value(0)
    transistor_tens.value(1)

# Fonction pour contrôler le servomoteur
def set_servo(angle):
    duty_cycle = int(angle*(7803-1950)/180) + 1950
    servo.duty_u16(duty_cycle)

# Lecture des données du capteur DHT11
def read_sensor_data():
    temperature, humidity = dht.read_data()
    return temperature, humidity

# Vérification des seuils et contrôle de la serre
def check_and_control():
    temperature, humidity = read_sensor_data()
    if temperature > TEMPERATURE_THRESHOLD or humidity > HUMIDITY_THRESHOLD:
        set_servo(180)  # Ouvrir la serre si les seuils sont dépassés
    else:
        set_servo(0)    # Fermer la serre sinon

# Création d'un point d'accès Wi-Fi avec le nom "serre" et le mot de passe "123456789"
def create_wifi_ap():
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    wlan.config(essid="serre", password="123456789")

# Route pour la page d'accueil du site Web
def index(client_socket):
    print("Programme Serre Connected!")
    temperature, humidity = read_sensor_data()
    html = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html>
<html>
<head><title>Serre Connectée</title></head>
<body>
<h1>Programme Serre Connected!</h1>
<p>Température: {} °C</p>
<p>Humidité: {} %</p>
</body>
</html>""".format(temperature, humidity)
    client_socket.write(html)

# Route pour le contrôle de la serre
def control(client_socket):
    request_data = client_socket.recv(1024)
    action = None
    if 'open' in request_data:
        action = 'open'
    elif 'close' in request_data:
        action = 'close'
    if action:
        if action == 'open':
            print("Serre Ouverte!")
            set_servo(180)
        elif action == 'close':
            print("Serre Fermée!")
            set_servo(0)
        response = "HTTP/1.1 204 No Content\r\n\r\n"
    else:
        response = "HTTP/1.1 400 Bad Request\r\n\r\n"
    client_socket.write(response)

def main():
    create_wifi_ap()  # Créer le point d'accès Wi-Fi au démarrage
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(addr)
    s.listen(1)

    while True:
        client_sock, client_addr = s.accept()
        print('Connexion depuis', client_addr)
        try:
            request_data = client_sock.recv(1024)
            if request_data:
                if 'GET / ' in request_data:
                    index(client_sock)
                elif 'POST /control' in request_data:
                    control(client_sock)
        except Exception as e:
            print("Erreur:", e)
        finally:
            client_sock.close()

if __name__ == "__main__":
    main()
