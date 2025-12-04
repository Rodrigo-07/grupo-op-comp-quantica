from text_converter import texto_para_numero, numero_para_texto

def encriptar_numero(m: int, e: int, n: int) -> int:
    m_encripitado = m**e % n
    
    return m_encripitado

def decriptar_numero(c: int, d: int, n: int) -> int:
    m_decripitado = c**d % n
    
    return m_decripitado

def encriptar_texto(texto: str, chave_publica: tuple[int, int]) -> list[int]:
    e, n = chave_publica # e é o expoente, n é o módulo
    
    numero = texto_para_numero(texto)
    
    encriptado = encriptar_numero(numero, e, n)
    
    return encriptado

def decriptar_texto(numero_criptografado: int, chave_privada: tuple[int, int]) -> str:
    
    d, n = chave_privada # d é o expoente, n é o módulo
    
    numero_decriptado = decriptar_numero(numero_criptografado, d, n)
    
    texto = numero_para_texto(numero_decriptado)
    
    return texto