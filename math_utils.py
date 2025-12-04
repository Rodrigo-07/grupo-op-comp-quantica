import math
def mdc(a, b):
    """
    Entrada: dois inteiros a, b
    Saída: int (máximo divisor comum)
    Exemplo: mdc(48, 18) → 6
    """
    if b == 0:
        return a
    else:
        return math.gcd(b, (a % b))
    

def inverso_multiplicativo(e, phi_n):
    """
    Entrada: e (int), phi_n (int)
    Saída: d (int) tal que (e * d) % phi_n == 1
    Exemplo: inverso_multiplicativo(7, 40) → 23
    """
    if mdc(e,phi_n) != 1:
        raise Exception("e não é coprimo de phi_n")
    for i in range(phi_n,3,-1):
        if i*e %phi_n ==1:
            return i
        



def eh_primo(n):
    """
    Entrada: n (int)
    Saída: bool (True se primo, False se não)
    Exemplo: eh_primo(17) → True
    """
    number = int(math.sqrt(n))
    for i in range(3,number+1):
        
        if n % i == 0:
            return False
        
    return True

if __name__ =="__main__":
    print(eh_primo(9999995))
    print(mdc(4,9999995))
    print(inverso_multiplicativo(7, 40))