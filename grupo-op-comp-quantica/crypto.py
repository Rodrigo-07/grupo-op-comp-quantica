from text_converter import texto_para_numero, numero_para_texto

def encriptar_numero(m: int, e: int, n: int) -> int:
    # Usa exponenciação modular para eficiência: (m^e) % n
    m_encripitado = pow(m, e, n)
    return m_encripitado

def decriptar_numero(c: int, d: int, n: int) -> int:
    # Usa exponenciação modular para eficiência: (c^d) % n
    m_decripitado = pow(c, d, n)
    return m_decripitado

def encriptar_texto(texto: str, chave_publica: tuple[int, int]) -> list[int]:
    e, n = chave_publica 
    
    numero = texto_para_numero(texto)
    
    encriptado = encriptar_numero(numero, e, n)
    
    return encriptado

def decriptar_texto(numero_criptografado: int, chave_privada: tuple[int, int]) -> str:
    
    d, n = chave_privada 
    
    numero_decriptado = decriptar_numero(numero_criptografado, d, n)
    
    texto = numero_para_texto(numero_decriptado)
    
    return texto