import random
from math_utils import mdc, inverso_multiplicativo, eh_primo

def gerar_primo(bits=8):
    minimo = 2 ** (bits - 1)
    maximo = 2 ** bits - 1
    
    while True:
        candidato = random.randint(minimo, maximo)
        if candidato % 2 == 0:
            candidato += 1
            
        if eh_primo(candidato):
            return candidato

def gerar_chaves(tamanho_bits=8):

    p = gerar_primo(tamanho_bits)
    q = gerar_primo(tamanho_bits)
    
    while p == q:
        q = gerar_primo(tamanho_bits)
    
    n = p * q
    
    phi_n = (p - 1) * (q - 1)
    
    e = 65537
    
    if e >= phi_n or mdc(e, phi_n) != 1:
        e = random.randrange(3, phi_n, 2)
        while mdc(e, phi_n) != 1:
            e = random.randrange(3, phi_n, 2)
    
    d = inverso_multiplicativo(e, phi_n)
    
    chave_publica = (e, n)
    chave_privada = (d, n)
    
    return (chave_publica, chave_privada)