from dataclasses import asdict
from datetime import timezone
from fastapi import APIRouter, HTTPException, status

import oqs

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.pqc_sessions import pqc_session_manager
from app.models import (
    Message,
    PQCKEMAlgorithm,
    PQCKEMAlgorithms,
    PQCKEMHandshakeRequest,
    PQCKEMHandshakeResponse,
    PQCHandshakeInitRequest,
    PQCHandshakeInitResponse,
    PQCHandshakeCompleteRequest,
    PQCHandshakeCompleteResponse,
)
from app.services.pqc import PQCService, _b64encode, _b64decode

router = APIRouter(prefix="/pqc", tags=["pqc"])
service = PQCService()


@router.get("/kems", response_model=PQCKEMAlgorithms)
def list_kem_algorithms() -> PQCKEMAlgorithms:
    """
    Lista todos os algoritmos KEM (Key Encapsulation Mechanism) disponíveis.
    
    Algoritmos pós-quânticos resistem a ataques de computadores quânticos
    usando problemas matemáticos diferentes (lattices, códigos, etc).
    
    Exemplos:
    - Kyber512/768/1024: Vencedor NIST, eficiente e seguro
    - BIKE: Baseado em códigos, chaves compactas
    - Classic-McEliece: Ultra conservador, chaves grandes
    """
    kems = [
        PQCKEMAlgorithm(**asdict(details))
        for details in service.list_kem_algorithms()
    ]
    return PQCKEMAlgorithms(data=kems)


@router.post("/handshake/init", response_model=PQCHandshakeInitResponse)
def init_pqc_handshake(
    payload: PQCHandshakeInitRequest,
    current_user: CurrentUser,
) -> PQCHandshakeInitResponse:
    """
    ETAPA 1: Inicia handshake PQC (requer JWT válido).
    
    Fluxo:
    1. Servidor gera par de chaves KEM
    2. Retorna handshake_id e chave pública
    3. Cliente deve encapsular segredo e chamar /handshake/complete
    
    Segurança:
    - Requer autenticação JWT (usuário logado)
    - Chave privada armazenada temporariamente (2 minutos)
    - Handshake_id único e seguro
    """
    algorithm = payload.algorithm or settings.DEFAULT_PQC_KEM
    
    try:
        # Gera par de chaves KEM
        keypair = service.generate_keypair(algorithm)
        
        # Cria handshake pendente
        handshake = pqc_session_manager.create_pending_handshake(
            user_id=current_user.id,
            algorithm=algorithm,
            secret_key=keypair.secret_key,
            public_key=keypair.public_key,
        )
        
        return PQCHandshakeInitResponse(
            handshake_id=handshake.handshake_id,
            algorithm=algorithm,
            public_key=_b64encode(keypair.public_key),
            expires_at=handshake.expires_at.isoformat(),
        )
        
    except oqs.MechanismNotSupportedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"KEM algorithm '{algorithm}' is not available: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate KEM keypair: {exc}",
        ) from exc


@router.post("/handshake/complete", response_model=PQCHandshakeCompleteResponse)
def complete_pqc_handshake(
    payload: PQCHandshakeCompleteRequest,
    current_user: CurrentUser,
) -> PQCHandshakeCompleteResponse:
    """
    ETAPA 2: Completa handshake PQC e cria sessão segura.
    
    Fluxo:
    1. Cliente envia ciphertext (segredo encapsulado)
    2. Servidor decapsula usando chave privada
    3. Ambos agora compartilham o mesmo segredo
    4. Sessão PQC criada com TTL de 5 minutos
    
    Segurança:
    - Valida que handshake pertence ao usuário atual
    - Shared secret nunca é transmitido (apenas hash armazenado)
    - Chave privada descartada após uso
    """
    # Recupera handshake pendente
    handshake = pqc_session_manager.get_pending_handshake(payload.handshake_id)
    
    if not handshake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Handshake not found or expired",
        )
    
    # Valida que o handshake pertence ao usuário atual
    if handshake.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Handshake does not belong to current user",
        )
    
    try:
        # Decodifica ciphertext enviado pelo cliente
        ciphertext = _b64decode(payload.ciphertext)
        
        # Decapsula segredo usando chave privada
        shared_secret = service.decapsulate_secret(
            algorithm=handshake.algorithm,
            secret_key=handshake.secret_key,
            ciphertext=ciphertext,
        )
        
        # Completa handshake e cria sessão PQC
        session = pqc_session_manager.complete_handshake(
            handshake_id=payload.handshake_id,
            shared_secret=shared_secret,
        )
        
        return PQCHandshakeCompleteResponse(
            session_id=session.session_id,
            expires_at=session.expires_at.isoformat(),
            message="PQC session established successfully",
        )
        
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to complete handshake: {exc}",
        ) from exc


@router.delete("/session/{session_id}", response_model=Message)
def revoke_pqc_session(
    session_id: str,
    current_user: CurrentUser,
) -> Message:
    """
    Revoga uma sessão PQC específica.
    
    Útil para "logout PQC" sem afetar a autenticação JWT principal.
    """
    session = pqc_session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )
    
    # Valida que a sessão pertence ao usuário
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to current user",
        )
    
    pqc_session_manager.revoke_session(session_id)
    return Message(message="PQC session revoked successfully")


@router.get("/sessions/stats")
def get_pqc_stats(current_user: CurrentUser) -> dict:
    """
    Estatísticas sobre sessões PQC (útil para monitoramento).
    
    Requer autenticação JWT.
    """
    return pqc_session_manager.get_stats()


# ============================================================================
# ENDPOINT DE DEMONSTRAÇÃO (apenas para testes/debug)
# ============================================================================

@router.post("/kem/handshake", response_model=PQCKEMHandshakeResponse)
def generate_kem_handshake(
    payload: PQCKEMHandshakeRequest | None = None,
) -> PQCKEMHandshakeResponse:
    """
    ⚠️  DEMONSTRAÇÃO APENAS - NÃO USAR EM PRODUÇÃO!
    
    Este endpoint executa um handshake KEM completo e EXPÕE ambos
    os segredos (cliente e servidor) para fins educacionais.
    
    Em produção, use:
    1. POST /pqc/handshake/init
    2. POST /pqc/handshake/complete
    
    Útil para entender como KEM funciona e validar implementações.
    """
    algorithm = (
        payload.algorithm if payload and payload.algorithm else settings.DEFAULT_PQC_KEM
    )
    try:
        handshake = service.generate_kem_handshake(algorithm)
    except oqs.MechanismNotSupportedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"KEM algorithm '{algorithm}' is not available: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to perform KEM handshake: {exc}",
        ) from exc

    details = PQCKEMAlgorithm(**asdict(handshake.details))
    return PQCKEMHandshakeResponse(
        algorithm=handshake.algorithm,
        public_key=handshake.public_key,
        ciphertext=handshake.ciphertext,
        server_shared_secret=handshake.server_shared_secret,
        client_shared_secret=handshake.client_shared_secret,
        shared_secret_match=handshake.shared_secret_match,
        details=details,
    )
