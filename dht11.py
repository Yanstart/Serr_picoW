import time
import RPi.GPIO as GPIO

class DHT11:
    def __init__(self, pin_name, display, servo_control):
        self.N1 = Pin(pin_name, Pin.OUT)
        self.PinName = pin_name
        self.display = display  # Référence vers l'objet Display
        self.servo_control = servo_control  # Référence vers l'objet ServoControl
        sleep_ms(10)
        self.last_temperature = None  # Stocke la dernière température affichée

    def read_data(self):
        self.__init__(self.PinName)
        data=[]
        j=0
        N1=self.N1
        N1.low()
        sleep_ms(20)
        N1.high()
        N1 = Pin(self.PinName, Pin.IN)
        sleep_us(30)
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
            j += 1
        print('Sensor is working')
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
            print('temperature is', temperature, '-wet is', humidity, '%')
        else:
            print('Error:', humidity, humidity_point, temperature, temperature_point, check)
        # Vérifie si la température est différente de celle précédemment affichée
        if temperature != self.last_temperature:
            # Affiche la température sur les 7 segments
            self.display.display_temperature(temperature)
            # Contrôle du servo moteur en fonction de la température
            self.servo_control.control_servo(temperature)
            # Stocke la température actuelle comme dernière température affichée
            self.last_temperature = temperature

        return [str(temperature), str(humidity)]
