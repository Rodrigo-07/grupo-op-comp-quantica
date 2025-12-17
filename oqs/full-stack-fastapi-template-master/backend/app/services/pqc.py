from __future__ import annotations

import base64
from dataclasses import dataclass
import uuid

import oqs


def _b64encode(value: bytes) -> str:
    """Keep JSON payloads binary-safe."""
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(value.encode("ascii"))


@dataclass(slots=True)
class KEMDetails:
    name: str
    claimed_nist_level: int
    is_classical_secured: bool
    length_public_key: int
    length_secret_key: int
    length_ciphertext: int
    length_shared_secret: int


@dataclass(slots=True)
class KEMHandshake:
    algorithm: str
    public_key: str
    ciphertext: str
    server_shared_secret: str
    client_shared_secret: str
    shared_secret_match: bool
    details: KEMDetails


@dataclass(slots=True)
class KEMKeyPair:
    """Par de chaves KEM gerado pelo servidor."""
    algorithm: str
    public_key: bytes
    secret_key: bytes


class PQCService:
    """
    Serviço de criptografia pós-quântica usando liboqs.
    
    Implementa Key Encapsulation Mechanism (KEM) para estabelecer
    segredos compartilhados resistentes a ataques quânticos.
    
    Fluxo de segurança:
    1. Servidor gera par de chaves KEM (generate_keypair)
    2. Cliente encapsula segredo usando chave pública (encapsulate_secret)
    3. Servidor decapsula usando chave privada (decapsulate_secret)
    4. Ambos compartilham o mesmo segredo sem transmiti-lo
    """

    def list_kem_algorithms(self) -> list[KEMDetails]:
        """
        Lista todos os algoritmos KEM disponíveis no liboqs.
        
        Exemplos populares:
        - Kyber512/768/1024: Finalista NIST, rápido e eficiente
        - BIKE: Baseado em códigos, chaves menores
        - Classic-McEliece: Conservador, chaves muito grandes
        """
        return [
            self._build_kem_details(algorithm)
            for algorithm in oqs.get_enabled_kem_mechanisms()
        ]

    def generate_keypair(self, algorithm: str) -> KEMKeyPair:
        """
        Gera um par de chaves KEM (pública + privada).
        
        A chave pública será enviada ao cliente.
        A chave privada deve ser guardada temporariamente para decapsular.
        """
        with oqs.KeyEncapsulation(algorithm) as kem:
            public_key = kem.generate_keypair()
            # IMPORTANTE: export_secret_key() extrai a chave privada
            secret_key = kem.export_secret_key()
        
        return KEMKeyPair(
            algorithm=algorithm,
            public_key=public_key,
            secret_key=secret_key,
        )
    
    def encapsulate_secret(self, algorithm: str, public_key_b64: str) -> tuple[bytes, bytes]:
        """
        Cliente: Encapsula um segredo usando a chave pública do servidor.
        
        Retorna:
        - ciphertext: enviado de volta ao servidor
        - shared_secret: usado localmente pelo cliente
        """
        public_key = _b64decode(public_key_b64)
        
        with oqs.KeyEncapsulation(algorithm) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
        
        return ciphertext, shared_secret
    
    def decapsulate_secret(
        self,
        algorithm: str,
        secret_key: bytes,
        ciphertext: bytes,
    ) -> bytes:
        """
        Servidor: Decapsula o segredo usando a chave privada.
        
        O shared_secret resultante será idêntico ao do cliente,
        provando que ambos completaram o handshake KEM.
        """
        with oqs.KeyEncapsulation(algorithm) as kem:
            # Restaura a chave privada no contexto KEM
            kem_with_key = oqs.KeyEncapsulation(algorithm, secret_key)
            shared_secret = kem_with_key.decap_secret(ciphertext)
        
        return shared_secret

    def generate_kem_handshake(self, algorithm: str) -> KEMHandshake:
        """
        DEMONSTRAÇÃO: Handshake completo em uma única chamada.
        
        ⚠️  APENAS PARA TESTES/DEBUG!
        
        Em produção, use o fluxo de duas etapas:
        1. generate_keypair() - servidor
        2. encapsulate_secret() - cliente
        3. decapsulate_secret() - servidor
        
        Este método expõe ambos os segredos para fins didáticos.
        """
        details = self._build_kem_details(algorithm)
        with oqs.KeyEncapsulation(algorithm) as server:
            public_key = server.generate_keypair()
            with oqs.KeyEncapsulation(algorithm) as client:
                ciphertext, client_shared_secret = client.encap_secret(public_key)
            server_shared_secret = server.decap_secret(ciphertext)

        return KEMHandshake(
            algorithm=algorithm,
            public_key=_b64encode(public_key),
            ciphertext=_b64encode(ciphertext),
            server_shared_secret=_b64encode(server_shared_secret),
            client_shared_secret=_b64encode(client_shared_secret),
            shared_secret_match=server_shared_secret == client_shared_secret,
            details=details,
        )

    def _build_kem_details(self, algorithm: str) -> KEMDetails:
        """Extrai detalhes de um algoritmo KEM."""
        with oqs.KeyEncapsulation(algorithm) as kem:
            return KEMDetails(
                name=algorithm,
                claimed_nist_level=kem.details['claimed_nist_level'],
                is_classical_secured=kem.details.get('ind_cca2', False),
                length_public_key=kem.details['length_public_key'],
                length_secret_key=kem.details['length_secret_key'],
                length_ciphertext=kem.details['length_ciphertext'],
                length_shared_secret=kem.details['length_shared_secret'],
            )
