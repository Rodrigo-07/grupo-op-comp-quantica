# Implementação RSA

Implementação completa do algoritmo de criptografia RSA (Rivest-Shamir-Adleman) desenvolvida do zero, sem uso de bibliotecas de criptografia externas.

## 👥 Integrantes

* **Ever Costa**
* **Gabriel Pelinsari**
* **Leandro Gomes**
* **Paula Piva**
* **Rodrigo**

---

## 🎯 Objetivo

Desenvolver uma implementação funcional e educacional do algoritmo RSA, cobrindo:
- Geração de números primos
- Criação de chaves pública e privada
- Conversão de texto para números
- Encriptação e decriptação de mensagens
- Interface de usuário via terminal

---

## 📁 Estrutura do Projeto

```
grupo-op-comp-quantica/
│
├── math_utils.py         
├── key_generation.py      
├── text_converter.py     
├── crypto.py             
├── main.py                
│
├── tests/                 
│   ├── test_math_utils.py
│   ├── test_key_generation.py
│   ├── test_text_converter.py
│   ├── test_crypto.py
│   └── test_integration.py
│
└── README.md
```

---

## 🔧 Divisão de Tarefas

### **Pessoa 1: Ever - Utilitários Matemáticos**
**Arquivo:** `math_utils.py`

**Responsabilidades:**
- Implementar cálculo do MDC (Máximo Divisor Comum) usando algoritmo de Euclides
- Implementar cálculo do inverso multiplicativo usando algoritmo estendido de Euclides
- Implementar verificação de primalidade

**Funções a implementar:**

```python
def mdc(a, b):
    """
    Calcula o Máximo Divisor Comum usando algoritmo de Euclides.
    
    Entrada: 
        a (int): primeiro número
        b (int): segundo número
    
    Saída: 
        int: MDC de a e b
    
    Exemplo:
        >>> mdc(48, 18)
        6
    """
    pass


def inverso_multiplicativo(e, phi_n):
    """
    Calcula o inverso multiplicativo de e módulo phi_n.
    Usa o algoritmo estendido de Euclides.
    
    Entrada:
        e (int): número para encontrar o inverso
        phi_n (int): módulo
    
    Saída:
        int: d tal que (e * d) % phi_n == 1
        None: se não existir inverso
    
    Exemplo:
        >>> inverso_multiplicativo(7, 40)
        23
    """
    pass


def eh_primo(n, k=5):
    """
    Verifica se n é primo usando teste de Miller-Rabin.
    
    Entrada:
        n (int): número a ser testado
        k (int): número de iterações (maior = mais preciso)
    
    Saída:
        bool: True se provavelmente primo, False se composto
    
    Exemplo:
        >>> eh_primo(17)
        True
        >>> eh_primo(18)
        False
    """
    pass
```

**Critérios de conclusão:**
- ✅ Todas as funções passam em testes unitários
- ✅ Arquivo `test_math_utils.py` criado com pelo menos 5 casos de teste por função

---

### **Pessoa 2: Paula - Geração de Chaves**
**Arquivo:** `key_generation.py`

**Responsabilidades:**
- Gerar números primos aleatórios
- Implementar o processo completo de geração de chaves RSA
- Escolher expoente público adequado

**Funções a implementar:**

```python
from math_utils import mdc, inverso_multiplicativo, eh_primo
import random


def gerar_primo(bits=16):
    """
    Gera um número primo aleatório com quantidade específica de bits.
    
    Entrada:
        bits (int): número de bits do primo desejado
    
    Saída:
        int: número primo aleatório
    
    Exemplo:
        >>> p = gerar_primo(16)
        >>> eh_primo(p)
        True
    """
    pass


def gerar_chaves(tamanho_bits=16):
    """
    Gera par de chaves RSA (pública e privada).
    
    Processo:
    1. Gera dois primos p e q
    2. Calcula n = p * q
    3. Calcula phi_n = (p-1) * (q-1)
    4. Escolhe e coprimo com phi_n (geralmente 65537)
    5. Calcula d = inverso de e módulo phi_n
    
    Entrada:
        tamanho_bits (int): tamanho em bits de p e q
    
    Saída:
        tuple: ((e, n), (d, n))
               chave_publica = (e, n)
               chave_privada = (d, n)
    
    Exemplo:
        >>> pub, priv = gerar_chaves(16)
        >>> pub  # (e, n)
        (65537, 3233)
        >>> priv  # (d, n)
        (2753, 3233)
    """
    pass


def salvar_chaves(chave_publica, chave_privada, arquivo_pub="public.key", arquivo_priv="private.key"):
    """
    Salva as chaves em arquivos (OPCIONAL - Bônus).
    
    Entrada:
        chave_publica (tuple): (e, n)
        chave_privada (tuple): (d, n)
        arquivo_pub (str): nome do arquivo para chave pública
        arquivo_priv (str): nome do arquivo para chave privada
    """
    pass
```

**Critérios de conclusão:**
- ✅ Geração de chaves funciona corretamente
- ✅ Chaves geradas são válidas (e e d são inversos módulo phi_n)
- ✅ Arquivo de teste criado

---

### **Pessoa 3: Leandro Gomes - Conversão Texto ↔ Números**
**Arquivo:** `text_converter.py`

**Responsabilidades:**
- Converter texto em lista de números (usando ASCII/UTF-8)
- Converter números de volta para texto
- Lidar com caracteres especiais e acentuação

**Funções a implementar:**

```python
def texto_para_numeros(texto):
    """
    Converte string em lista de códigos numéricos (ASCII/UTF-8).
    
    Entrada:
        texto (str): texto a ser convertido
    
    Saída:
        list[int]: lista com código de cada caractere
    
    Exemplo:
        >>> texto_para_numeros("OI")
        [79, 73]
        >>> texto_para_numeros("Olá!")
        [79, 108, 225, 33]
    """
    pass


def numeros_para_texto(numeros):
    """
    Converte lista de números de volta para string.
    
    Entrada:
        numeros (list[int]): lista de códigos numéricos
    
    Saída:
        str: texto reconstruído
    
    Exemplo:
        >>> numeros_para_texto([79, 73])
        "OI"
        >>> numeros_para_texto([79, 108, 225, 33])
        "Olá!"
    """
    pass


def validar_mensagem(numeros, n):
    """
    Verifica se todos os números da mensagem são menores que n.
    (Necessário para RSA funcionar corretamente)
    
    Entrada:
        numeros (list[int]): códigos da mensagem
        n (int): módulo RSA
    
    Saída:
        bool: True se todos < n, False caso contrário
    
    Exemplo:
        >>> validar_mensagem([65, 66, 67], 100)
        True
        >>> validar_mensagem([65, 66, 67], 50)
        False
    """
    pass
```

**Critérios de conclusão:**
- ✅ Conversão funciona para textos simples e com acentuação
- ✅ Conversão é reversível (texto → números → texto = texto original)
- ✅ Validação identifica mensagens incompatíveis com n

---

### **Pessoa 4: Rodrigo - Criptografia**
**Arquivo:** `crypto.py`

**Responsabilidades:**
- Implementar encriptação de números individuais
- Implementar decriptação de números individuais
- Integrar com conversão de texto para processar mensagens completas

**Funções a implementar:**

```python
from text_converter import texto_para_numeros, numeros_para_texto, validar_mensagem


def encriptar_numero(m, e, n):
    """
    Encripta um único número usando RSA.
    Fórmula: c = (m^e) mod n
    
    Entrada:
        m (int): mensagem (número)
        e (int): expoente público
        n (int): módulo
    
    Saída:
        int: número criptografado
    
    Exemplo:
        >>> encriptar_numero(65, 7, 3233)
        2790
    
    DICA: Use pow(m, e, n) para calcular (m^e) mod n eficientemente
    """
    pass


def decriptar_numero(c, d, n):
    """
    Decripta um único número usando RSA.
    Fórmula: m = (c^d) mod n
    
    Entrada:
        c (int): cifra (número criptografado)
        d (int): expoente privado
        n (int): módulo
    
    Saída:
        int: mensagem original
    
    Exemplo:
        >>> decriptar_numero(2790, 2753, 3233)
        65
    """
    pass

```

**Critérios de conclusão:**
- ✅ Encriptação e decriptação funcionam corretamente
- ✅ Texto encriptado e decriptado retorna ao original
- ✅ Tratamento de erros para mensagens inválidas

---

### **Pessoa 5: Gabriel - Interface Principal**
**Arquivo:** `main.py`

**Responsabilidades:**
- Criar interface de usuário no terminal
- Integrar todos os módulos
- Gerenciar fluxo do programa
- Tratar erros e validações de entrada

**Funções a implementar:**

```python
from key_generation import gerar_chaves, salvar_chaves
from crypto import encriptar_texto, decriptar_texto


def exibir_menu():
    """
    Exibe o menu principal de opções.
    """
    print("\n" + "="*50)
    print("🔐 SISTEMA DE CRIPTOGRAFIA RSA")
    print("="*50)
    print("1. Gerar novas chaves")
    print("2. Encriptar mensagem")
    print("3. Decriptar mensagem")
    print("4. Exibir chaves atuais")
    print("5. Sobre o RSA")
    print("0. Sair")
    print("="*50)


def gerar_novas_chaves():
    """
    Solicita tamanho de bits e gera novo par de chaves.
    Exibe as chaves geradas.
    """
    pass


def encriptar_mensagem_interface(chave_publica):
    """
    Solicita mensagem do usuário e encripta usando chave pública.
    Exibe o resultado criptografado.
    
    Entrada:
        chave_publica (tuple): (e, n)
    """
    pass


def decriptar_mensagem_interface(chave_privada):
    """
    Solicita mensagem criptografada e decripta usando chave privada.
    Exibe o texto original.
    
    Entrada:
        chave_privada (tuple): (d, n)
    """
    pass


def exibir_chaves(chave_publica, chave_privada):
    """
    Mostra as chaves atuais de forma formatada.
    """
    pass


def sobre_rsa():
    """
    Exibe informações educacionais sobre o RSA.
    """
    pass


def main():
    """
    Função principal que gerencia o fluxo do programa.
    
    Fluxo:
    1. Gera chaves iniciais (ou carrega se existirem)
    2. Exibe menu
    3. Processa escolha do usuário
    4. Repete até usuário sair
    """
    chave_publica = None
    chave_privada = None
    
    print("Bem-vindo ao Sistema RSA!")
    print("Gerando chaves iniciais...")
    
    # TODO: Implementar lógica completa
    
    while True:
        exibir_menu()
        # TODO: Processar escolhas
        pass


if __name__ == "__main__":
    main()
```

**Critérios de conclusão:**
- ✅ Interface intuitiva e fácil de usar
- ✅ Tratamento de erros e validações
- ✅ Todas as funcionalidades acessíveis pelo menu
- ✅ Mensagens claras para o usuário

---

## 🚀 Instruções de Desenvolvimento

### Fase 1: Desenvolvimento Individual
1. Cada pessoa implementa seu módulo
2. Criar arquivo de teste para validar funções
3. Documentar código com comentários
4. Testar individualmente antes de integrar

### Fase 2: Testes Finais 
1. Testar fluxo completo: gerar chaves → encriptar → decriptar
2. Testar casos extremos (textos longos, caracteres especiais)
3. Revisar documentação
4. Preparar demonstração

---

## 📋 Como Executar

### Requisitos
- Python 3.7 ou superior
- Nenhuma biblioteca externa necessária (apenas stdlib)

### Execução

```bash
# Clone ou baixe o repositório
cd rsa-python

# Execute o programa principal
python main.py
```

### Exemplo de Uso

```
🔐 SISTEMA DE CRIPTOGRAFIA RSA
==================================================
1. Gerar novas chaves
2. Encriptar mensagem
3. Decriptar mensagem
4. Exibir chaves atuais
5. Sobre o RSA
0. Sair
==================================================
Escolha uma opção: 2

Digite a mensagem para encriptar: Olá, mundo!
Mensagem criptografada: [2234, 1876, 3421, ...]

Deseja decriptar agora? (s/n): s
Mensagem original: Olá, mundo!
```

---

## 📚 Conceitos Implementados

### Algoritmo RSA
1. **Geração de Chaves:**
   - Escolher dois primos p e q
   - Calcular n = p × q
   - Calcular φ(n) = (p-1)(q-1)
   - Escolher e coprimo com φ(n)
   - Calcular d = inverso de e módulo φ(n)

2. **Encriptação:**
   - c ≡ m^e (mod n)

3. **Decriptação:**
   - m ≡ c^d (mod n)

### Conceitos Matemáticos
- Números primos
- Congruência modular
- Inverso multiplicativo
- Teorema de Euler
- Algoritmo de Euclides

---

## ⚠️ Limitações e Considerações

- **Tamanho de chave:** Para fins educacionais, usar chaves pequenas (16-32 bits)
- **Segurança:** Esta implementação é EDUCACIONAL, não usar em produção
- **Performance:** Números muito grandes podem ser lentos
- **Caracteres:** Suporta UTF-8, mas números devem ser < n

---

## 🤝 Contribuições

Desenvolvido como projeto acadêmico por:
- Ever Costa
- Gabriel Pelinsari
- Leandro Gomes
- Paula Piva
- Rodrigo
