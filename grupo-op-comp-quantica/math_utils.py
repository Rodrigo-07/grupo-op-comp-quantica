import math
import random

def mdc(a, b):
    """
    Entrada: dois inteiros a, b
    Saída: int (máximo divisor comum)
    Exemplo: mdc(48, 18) → 6
    """
    return math.gcd(a, b)

def inverso_multiplicativo(e, phi_n):
    """
    Entrada: e (int), phi_n (int)
    Saída: d (int) tal que (e * d) % phi_n == 1
    Usa o Algoritmo de Euclides Estendido.
    """
    t, newt = 0, 1
    r, newr = phi_n, e

    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr

    if r > 1:
        raise Exception("e não é invertível (não é coprimo de phi_n)")
    
    if t < 0:
        t = t + phi_n

    return t

def eh_primo(n, k=40):
    """
    Entrada: n (int), k (int) - número de testes
    Saída: bool (True se provavelmente primo, False se composto)
    Usa o teste de Miller-Rabin.
    """
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # Escreve n-1 como 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

if __name__ =="__main__":
    print(eh_primo(9999995))
    print(mdc(4,9999995))
    print(inverso_multiplicativo(7, 40))