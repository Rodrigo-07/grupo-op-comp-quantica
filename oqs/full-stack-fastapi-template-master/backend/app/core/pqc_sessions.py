"""
Gerenciador de Sessões PQC (Post-Quantum Cryptography)

Este módulo implementa um gerenciador de sessões em memória para autenticação
pós-quântica usando algoritmos KEM (Key Encapsulation Mechanism).

Arquitetura de Segurança:
1. Cliente autentica via JWT tradicional (login normal)
2. Para ações sensíveis, cliente inicia handshake PQC
3. Servidor valida JWT + Sessão PQC ativa

Vantagens:
- Proteção contra futuros computadores quânticos
- Step-up security: PQC apenas quando necessário
- Sessões de curta duração (5 min) minimizam janela de ataque
- Shared secret nunca é transmitido (apenas hash armazenado)
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

from app.core.config import settings


@dataclass
class PendingHandshake:
    """
    Representa um handshake PQC em andamento (primeira etapa).
    
    Armazena a chave privada temporariamente até o cliente
    completar o handshake enviando o ciphertext.
    """
    handshake_id: str
    user_id: uuid.UUID
    algorithm: str
    secret_key: bytes  # Chave privada KEM (temporária)
    public_key: bytes
    created_at: datetime
    expires_at: datetime


@dataclass
class PQCSession:
    """
    Representa uma sessão PQC ativa após handshake completo.
    
    Segurança:
    - Armazena apenas HASH do shared secret (nunca o segredo em si)
    - TTL curto (5 minutos) força renovação frequente
    - Vinculada ao user_id para validação adicional
    """
    session_id: str
    user_id: uuid.UUID
    algorithm: str
    shared_secret_hash: str  # SHA-256 do shared secret
    created_at: datetime
    expires_at: datetime


class PQCSessionManager:
    """
    Gerenciador de sessões PQC em memória.
    
    NOTA: Para produção, considere usar Redis ou similar para:
    - Compartilhar sessões entre múltiplas instâncias da API
    - Persistência além da memória do processo
    - Melhor performance em escala
    """
    
    def __init__(self):
        # Handshakes pendentes (aguardando ciphertext do cliente)
        self._pending_handshakes: Dict[str, PendingHandshake] = {}
        
        # Sessões PQC ativas
        self._active_sessions: Dict[str, PQCSession] = {}
    
    def create_pending_handshake(
        self,
        user_id: uuid.UUID,
        algorithm: str,
        secret_key: bytes,
        public_key: bytes,
    ) -> PendingHandshake:
        """
        Cria um handshake pendente (etapa 1 do handshake KEM).
        
        O cliente receberá a chave pública e o handshake_id.
        Ele deve encapsular um segredo e enviar o ciphertext de volta.
        """
        handshake_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        # Handshake pendente expira em 2 minutos
        expires_at = now + timedelta(minutes=2)
        
        handshake = PendingHandshake(
            handshake_id=handshake_id,
            user_id=user_id,
            algorithm=algorithm,
            secret_key=secret_key,
            public_key=public_key,
            created_at=now,
            expires_at=expires_at,
        )
        
        self._pending_handshakes[handshake_id] = handshake
        return handshake
    
    def get_pending_handshake(self, handshake_id: str) -> PendingHandshake | None:
        """
        Recupera um handshake pendente e remove expirados.
        """
        self._cleanup_expired_handshakes()
        return self._pending_handshakes.get(handshake_id)
    
    def complete_handshake(
        self,
        handshake_id: str,
        shared_secret: bytes,
    ) -> PQCSession:
        """
        Completa o handshake e cria uma sessão PQC ativa.
        
        Segurança:
        - Remove o handshake pendente (chave privada descartada)
        - Cria sessão com HASH do shared secret
        - Shared secret original não é armazenado
        """
        handshake = self._pending_handshakes.pop(handshake_id, None)
        if not handshake:
            raise ValueError("Handshake not found or expired")
        
        # Gera hash SHA-256 do shared secret
        secret_hash = hashlib.sha256(shared_secret).hexdigest()
        
        # Cria sessão PQC
        session_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.PQC_SESSION_TTL_MINUTES)
        
        session = PQCSession(
            session_id=session_id,
            user_id=handshake.user_id,
            algorithm=handshake.algorithm,
            shared_secret_hash=secret_hash,
            created_at=now,
            expires_at=expires_at,
        )
        
        self._active_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> PQCSession | None:
        """
        Recupera uma sessão PQC ativa.
        """
        self._cleanup_expired_sessions()
        return self._active_sessions.get(session_id)
    
    def validate_session(
        self,
        session_id: str,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Valida se uma sessão PQC está ativa e pertence ao usuário.
        
        Usado como dependency em rotas protegidas.
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Verifica se a sessão pertence ao usuário correto
        if session.user_id != user_id:
            return False
        
        # Verifica expiração
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            self._active_sessions.pop(session_id, None)
            return False
        
        return True
    
    def revoke_session(self, session_id: str) -> bool:
        """
        Revoga uma sessão PQC (logout PQC).
        """
        return self._active_sessions.pop(session_id, None) is not None
    
    def revoke_all_user_sessions(self, user_id: uuid.UUID) -> int:
        """
        Revoga todas as sessões PQC de um usuário.
        """
        sessions_to_remove = [
            sid for sid, session in self._active_sessions.items()
            if session.user_id == user_id
        ]
        
        for sid in sessions_to_remove:
            self._active_sessions.pop(sid, None)
        
        return len(sessions_to_remove)
    
    def _cleanup_expired_handshakes(self) -> None:
        """Remove handshakes expirados."""
        now = datetime.now(timezone.utc)
        expired = [
            hid for hid, h in self._pending_handshakes.items()
            if now > h.expires_at
        ]
        for hid in expired:
            self._pending_handshakes.pop(hid, None)
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove sessões expiradas."""
        now = datetime.now(timezone.utc)
        expired = [
            sid for sid, s in self._active_sessions.items()
            if now > s.expires_at
        ]
        for sid in expired:
            self._active_sessions.pop(sid, None)
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas sobre sessões (útil para monitoramento).
        """
        self._cleanup_expired_handshakes()
        self._cleanup_expired_sessions()
        
        return {
            "pending_handshakes": len(self._pending_handshakes),
            "active_sessions": len(self._active_sessions),
        }


# Singleton global do gerenciador de sessões
pqc_session_manager = PQCSessionManager()
