import sys
import time
from key_generation import gerar_chaves
from crypto import encriptar_texto, decriptar_texto
from text_converter import texto_para_numero

def exibir_menu():
    print("\n" + "="*50)
    print("🔐 SISTEMA DE CRIPTOGRAFIA RSA")
    print("="*50)
    print("1. 🚀 Simulação Rápida (Recomendado)")
    print("2. 🔑 Gerar novas chaves (Manual)")
    print("3. 🔒 Encriptar mensagem (Manual)")
    print("4. 🔓 Decriptar mensagem (Manual)")
    print("5. 👁️  Exibir chaves atuais")
    print("6. ℹ️  Sobre o RSA")
    print("0. Sair")
    print("="*50)

def simulacao_rapida():
    print("\n" + "-"*50)
    print("🚀 SIMULAÇÃO RÁPIDA RSA")
    print("   (Gera chaves automaticamente baseadas no tamanho do texto)")
    print("-" * 50)
    
    texto = input("Digite a palavra ou frase para testar: ")
    if not texto:
        print("Texto vazio. Voltando ao menu.")
        return

    print(f"\n[1/4] Analisando mensagem...")

    msg_bytes = texto.encode('utf-8')
    bits_msg = len(msg_bytes) * 8
    print(f"      Tamanho da mensagem: {len(msg_bytes)} bytes ({bits_msg} bits)")
    
    bits_primo = (bits_msg // 2) + 24 # Margem de segurança maior
    if bits_primo < 32: bits_primo = 32 # Mínimo de 32 bits para primos (chave de ~64 bits)

    print(f"      Calculando tamanho de chave necessário: Primos de {bits_primo} bits")

    print(f"\n[2/4] Gerando chaves RSA...")
    time.sleep(0.5)
    try:
        chave_publica, chave_privada = gerar_chaves(tamanho_bits=bits_primo)
        e, n = chave_publica
        d, _ = chave_privada
        print(f"      ✅ Chaves geradas!")
        print(f"      🔑 Pública (e={e}, n={n})")
        print(f"      🗝️  Privada (d={d}, n={n})")
    except Exception as err:
        print(f"      ❌ Erro ao gerar chaves: {err}")
        return

    print(f"\n[3/4] Encriptando...")
    time.sleep(0.5)
    try:
        num_msg = texto_para_numero(texto)
        print(f"      🔢 Texto convertido em número: {num_msg}")
        
        msg_cifrada = encriptar_texto(texto, chave_publica)
        print(f"      🔒 Mensagem Cifrada: {msg_cifrada}")
    except Exception as err:
        print(f"      ❌ Erro ao encriptar: {err}")
        return

    print(f"\n[4/4] Decriptando...")
    time.sleep(0.5)
    try:
        msg_decifrada = decriptar_texto(msg_cifrada, chave_privada)
        print(f"      🔓 Mensagem Decifrada: {msg_decifrada}")
        
        if msg_decifrada == texto:
            print(f"\n✅ SUCESSO: O ciclo completou perfeitamente!")
        else:
            print(f"\n⚠️  ALERTA: A mensagem decifrada é diferente da original.")
    except Exception as err:
        print(f"      ❌ Erro ao decriptar: {err}")

    input("\nPressione Enter para voltar ao menu...")

def menu_gerar_chaves():
    print("\n--- Gerando Novas Chaves (Manual) ---")
    print("Recomendado: 1024 bits ou mais para segurança real.")
    print("Para testes rápidos, 64 ou 128 bits são suficientes.")
    try:
        entrada = input("Digite o tamanho dos primos em bits (padrão 128): ")
        if not entrada:
            bits = 128
        else:
            bits = int(entrada)
            if bits < 8:
                print("Tamanho muito pequeno. Usando mínimo de 8 bits.")
                bits = 8
    except ValueError:
        print("Valor inválido. Usando padrão 128.")
        bits = 128
    
    print(f"Gerando chaves com primos de {bits} bits... Aguarde.")
    try:
        chave_publica, chave_privada = gerar_chaves(tamanho_bits=bits)
        print("Chaves geradas com sucesso!")
        return chave_publica, chave_privada
    except Exception as e:
        print(f"Erro ao gerar chaves: {e}")
        return None, None

def menu_encriptar(chave_publica):
    if not chave_publica:
        print("\nErro: Chaves não geradas. Gere as chaves primeiro (Opção 2) ou use a Simulação Rápida (Opção 1).")
        return

    print("\n--- Encriptar Mensagem ---")
    texto = input("Digite a mensagem para encriptar: ")
    
    e, n = chave_publica
    try:
        numero_msg = texto_para_numero(texto)
        if numero_msg >= n:
            print(f"\n⚠️  [AVISO CRÍTICO] ⚠️")
            print(f"A mensagem é muito longa para a chave atual!")
            print(f"Valor da mensagem: {numero_msg}")
            print(f"Módulo n da chave: {n}")
            print("O RSA só consegue recuperar a mensagem se Mensagem < n.")
            print("Sugestão: Gere chaves maiores (Opção 2) ou use a Simulação Rápida (Opção 1).")
            confirmar = input("Deseja continuar mesmo assim? (s/n): ")
            if confirmar.lower() != 's':
                return
    except Exception as e:
        print(f"Erro na conversão do texto: {e}")
        return

    try:
        mensagem_cifrada = encriptar_texto(texto, chave_publica)
        print(f"\nMensagem Criptografada (Inteiro): {mensagem_cifrada}")
    except Exception as e:
        print(f"Erro ao encriptar: {e}")

def menu_decriptar(chave_privada):
    if not chave_privada:
        print("\nErro: Chaves não geradas. Gere as chaves primeiro.")
        return

    print("\n--- Decriptar Mensagem ---")
    try:
        entrada = input("Digite o número criptografado: ")
        numero_cifrado = int(entrada)
        
        texto_decifrado = decriptar_texto(numero_cifrado, chave_privada)
        print(f"\nMensagem Original: {texto_decifrado}")
    except ValueError:
        print("Erro: A entrada deve ser um número inteiro válido.")
    except Exception as e:
        print(f"Erro ao decriptar: {e}")
        print("Verifique se a chave privada está correta.")

def exibir_chaves(chave_publica, chave_privada):
    if not chave_publica or not chave_privada:
        print("\nNenhuma chave gerada no momento.")
    else:
        print("\n--- Chaves Atuais ---")
        print(f"Chave Pública (e, n): {chave_publica}")
        print(f"Chave Privada (d, n): {chave_privada}")

def sobre_rsa():
    print("\n--- Sobre o RSA ---")
    print("Implementação didática do algoritmo RSA.")
    print("Esta implementação converte o texto inteiro para um único número.")
    print("Melhorias implementadas:")
    print("- Teste de primalidade Miller-Rabin para geração rápida de primos grandes.")
    print("- Algoritmo de Euclides Estendido para cálculo eficiente do inverso modular.")
    print("- Exponenciação modular para encriptação/decriptação rápida.")
    print("Importante: O valor numérico do texto deve ser menor que o módulo n da chave.")

def main():
    chave_publica = None
    chave_privada = None

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            simulacao_rapida()
        elif opcao == '2':
            res = menu_gerar_chaves()
            if res[0] is not None:
                chave_publica, chave_privada = res
                exibir_chaves(chave_publica, chave_privada)
        elif opcao == '3':
            menu_encriptar(chave_publica)
        elif opcao == '4':
            menu_decriptar(chave_privada)
        elif opcao == '5':
            exibir_chaves(chave_publica, chave_privada)
        elif opcao == '6':
            sobre_rsa()
        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
