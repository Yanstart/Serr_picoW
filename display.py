import machine
import time

class Display:
    def __init__(self):
        # Configuration des broches GPIO
        self.segments = (1, 2, 4, 5)
        self.selection_transistors = (19, 20)  # Assumant que ce sont les broches que vous avez spécifiées pour les transistors
        for segment in self.segments:
            machine.Pin(segment, machine.Pin.OUT)
        for transistor in self.selection_transistors:
            machine.Pin(transistor, machine.Pin.OUT)

        # Dictionnaire des configurations des segments pour chaque chiffre de 0 à 9
        self.digits = {
            0: (1, 1, 1, 1),
            1: (0, 1, 1, 0),
            2: (1, 1, 0, 1),
            3: (1, 1, 1, 0),
            4: (0, 1, 1, 0),
            5: (1, 0, 1, 1),
            6: (1, 0, 1, 1),
            7: (1, 1, 1, 0),
            8: (1, 1, 1, 1),
            9: (1, 1, 1, 0)
        }

        self.last_temperature = None  # Stocke la dernière température affichée

    def display_temperature(self, temperature):
        # Vérifie si la température est différente de celle précédemment affichée
        if temperature != self.last_temperature:
            # Divise la température en dizaines et unités
            tens = temperature // 10
            units = temperature % 10

            # Allume les segments correspondants aux dizaines
            pin_a = machine.Pin(1, machine.Pin.OUT)
            pin_a.value(1)  # Active le transistor pour le premier afficheur
            for segment, state in zip(self.segments, self.digits[tens]):
                machine.Pin(segment, machine.Pin.OUT).value(state)
            time.sleep(0.001)
            pin_a.value(0)  # Désactive le transistor pour le premier afficheur

            # Allume les segments correspondants aux unités
            pin_b = machine.Pin(5, machine.Pin.OUT)
            pin_b.value(1)  # Active le transistor pour le deuxième afficheur
            for segment, state in zip(self.segments, self.digits[units]):
                machine.Pin(segment, machine.Pin.OUT).value(state)
            time.sleep(0.001)
            pin_b.value(0)  # Désactive le transistor pour le deuxième afficheur

            # Stocke la température actuelle comme dernière température affichée
            self.last_temperature = temperature

        # Éteint tous les segments
        for segment in self.segments:
            machine.Pin(segment, machine.Pin.OUT).value(0)
