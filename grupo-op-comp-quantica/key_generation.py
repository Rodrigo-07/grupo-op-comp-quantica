import random
from math_utils import eh_primo

def gerar_primo(bits=8):
    minimo = 2 ** (bits - 1)
    maximo = 2 ** bits - 1
    
    while True:
        candidato = random.randint(minimo, maximo)
        if eh_primo(candidato):
            return candidato