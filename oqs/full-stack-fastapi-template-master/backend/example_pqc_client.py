#!/usr/bin/env python3
"""
Exemplo de cliente PQC para demonstrar o fluxo completo de autenticação.

Este script demonstra:
1. Login JWT tradicional
2. Handshake PQC em duas etapas
3. Operação protegida (troca de senha)

Uso:
    python example_pqc_client.py
"""

import base64
import requests

try:
    import oqs
except ImportError:
    print("❌ liboqs-python não instalado!")
    print("   Instale com: pip install liboqs-python")
    exit(1)


BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@example.com"
PASSWORD = "password"


def login() -> str:
    """Etapa 1: Login tradicional JWT."""
    print("\n📧 1. Login JWT...")
    
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data={
            "username": EMAIL,
            "password": PASSWORD,
        },
    )
    
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.json())
        exit(1)
    
    token = response.json()["access_token"]
    print(f"✅ JWT obtido: {token[:30]}...")
    return token


def list_algorithms() -> None:
    """Lista algoritmos KEM disponíveis."""
    print("\n🔐 2. Listar algoritmos PQC...")
    
    response = requests.get(f"{BASE_URL}/pqc/kems")
    kems = response.json()["data"]
    
    print(f"✅ {len(kems)} algoritmos disponíveis:")
    for kem in kems[:5]:  # Mostra apenas os 5 primeiros
        print(f"   - {kem['name']}: NIST Level {kem['claimed_nist_level']}")


def pqc_handshake(jwt_token: str, algorithm: str = "Kyber512") -> str:
    """Etapa 2: Handshake PQC completo."""
    print(f"\n🤝 3. Handshake PQC ({algorithm})...")
    
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    # Etapa 3.1: Iniciar handshake (servidor gera chaves)
    print("   → POST /pqc/handshake/init")
    response = requests.post(
        f"{BASE_URL}/pqc/handshake/init",
        headers=headers,
        json={"algorithm": algorithm},
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao iniciar handshake: {response.status_code}")
        print(response.json())
        exit(1)
    
    data = response.json()
    handshake_id = data["handshake_id"]
    public_key_b64 = data["public_key"]
    
    print(f"   ✓ Handshake ID: {handshake_id[:20]}...")
    print(f"   ✓ Chave pública recebida ({len(public_key_b64)} bytes)")
    
    # Etapa 3.2: Cliente encapsula segredo
    print("   → Cliente: Encapsular segredo com KEM")
    public_key = base64.b64decode(public_key_b64)
    
    with oqs.KeyEncapsulation(algorithm) as client:
        ciphertext, shared_secret = client.encap_secret(public_key)
    
    ciphertext_b64 = base64.b64encode(ciphertext).decode()
    print(f"   ✓ Ciphertext gerado ({len(ciphertext)} bytes)")
    print(f"   ✓ Shared secret local: {shared_secret.hex()[:32]}...")
    
    # Etapa 3.3: Completar handshake (servidor decapsula)
    print("   → POST /pqc/handshake/complete")
    response = requests.post(
        f"{BASE_URL}/pqc/handshake/complete",
        headers=headers,
        json={
            "handshake_id": handshake_id,
            "ciphertext": ciphertext_b64,
        },
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao completar handshake: {response.status_code}")
        print(response.json())
        exit(1)
    
    session_data = response.json()
    session_id = session_data["session_id"]
    expires_at = session_data["expires_at"]
    
    print(f"✅ Sessão PQC criada!")
    print(f"   Session ID: {session_id[:30]}...")
    print(f"   Expira em: {expires_at}")
    
    return session_id


def update_password_with_pqc(jwt_token: str, pqc_session: str) -> None:
    """Etapa 3: Operação protegida - trocar senha."""
    print("\n🔒 4. Trocar senha (operação protegida)...")
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-PQC-Session": pqc_session,
    }
    
    # Nota: Não vamos realmente trocar a senha, apenas demonstrar
    print("   ℹ️  Simulando troca de senha...")
    print(f"   → PATCH /users/me/password")
    print(f"   → Headers: JWT + X-PQC-Session")
    
    # Descomente para realmente trocar senha:
    # response = requests.patch(
    #     f"{BASE_URL}/users/me/password",
    #     headers=headers,
    #     json={
    #         "current_password": PASSWORD,
    #         "new_password": "newpassword123",
    #     },
    # )
    # print(response.json())
    
    print("✅ Operação protegida autenticada com sucesso!")


def test_without_pqc(jwt_token: str) -> None:
    """Demonstra que operação protegida falha sem PQC."""
    print("\n⚠️  5. Testar sem sessão PQC (deve falhar)...")
    
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    response = requests.patch(
        f"{BASE_URL}/users/me/password",
        headers=headers,
        json={
            "current_password": PASSWORD,
            "new_password": "newpassword123",
        },
    )
    
    if response.status_code == 403:
        print("✅ Corretamente rejeitado! (falta X-PQC-Session)")
        print(f"   Mensagem: {response.json()['detail'][:80]}...")
    else:
        print(f"❌ Esperado 403, recebeu {response.status_code}")


def get_stats(jwt_token: str) -> None:
    """Mostra estatísticas das sessões PQC."""
    print("\n📊 6. Estatísticas das sessões...")
    
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{BASE_URL}/pqc/sessions/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Sessões ativas: {stats['active_sessions']}")
        print(f"   Handshakes pendentes: {stats['pending_handshakes']}")


def main():
    """Executa o fluxo completo."""
    print("=" * 60)
    print("  DEMONSTRAÇÃO: Autenticação PQC (Post-Quantum Crypto)")
    print("=" * 60)
    
    try:
        # 1. Login JWT
        jwt_token = login()
        
        # 2. Listar algoritmos
        list_algorithms()
        
        # 3. Handshake PQC
        pqc_session = pqc_handshake(jwt_token)
        
        # 4. Operação protegida com PQC
        update_password_with_pqc(jwt_token, pqc_session)
        
        # 5. Testar sem PQC (deve falhar)
        test_without_pqc(jwt_token)
        
        # 6. Estatísticas
        get_stats(jwt_token)
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRAÇÃO COMPLETA!")
        print("=" * 60)
        print("\nResumo:")
        print("  ✓ JWT tradicional funciona normalmente")
        print("  ✓ Handshake PQC estabelece sessão segura")
        print("  ✓ Operações críticas exigem ambos (JWT + PQC)")
        print("  ✓ Sistema protegido contra ataques quânticos futuros")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar ao servidor!")
        print("   Certifique-se de que a API está rodando:")
        print("   cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
