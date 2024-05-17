import machine
import utime
# Pins connectées au décodeur 74LS47
pin_a = machine.Pin(1, machine.Pin.OUT)
pin_b = machine.Pin(2, machine.Pin.OUT)
pin_c = machine.Pin(4, machine.Pin.OUT)
pin_d = machine.Pin(5, machine.Pin.OUT)
# Pins connectées aux transistors pour les afficheurs 7 segments
transistor_units = machine.Pin(19, machine.Pin.OUT)
transistor_tens = machine.Pin(20, machine.Pin.OUT)
# Définition des séquences pour chaque chiffre sur les 7 segments
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
    utime.sleep_ms(5)  # Calibre le temps de basculement
    transistor_units.value(0)
    transistor_tens.value(1)
# Boucle principale pour afficher les chiffres en boucle
while True:
    # Récupérer le nombre à afficher depuis le terminal
    number = int(input("Entrez un nombre entre 0 et 99 : "))
    # Afficher les chiffres des unités et des dizaines
    tens = number // 10
    units = number % 10
    # Afficher le chiffre des dizaines
    display_digit(tens)
    toggle_digits()
    # Afficher le chiffre des unités
    display_digit(units)
    toggle_digits()
