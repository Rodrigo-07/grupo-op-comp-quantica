from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.pqc_sessions import pqc_session_manager
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def validate_pqc_session(
    current_user: CurrentUser,
    x_pqc_session: str = Header(..., description="PQC Session ID"),
) -> User:
    """
    Dependency para validar sessão PQC ativa.
    
    USO:
    Adicione esta dependency em rotas que exigem step-up security:
    
    @router.patch("/me/password")
    def update_password(user: Annotated[User, Depends(validate_pqc_session)]):
        ...
    
    SEGURANÇA:
    - Valida JWT (via CurrentUser)
    - Valida sessão PQC ativa no header X-PQC-Session
    - Verifica que a sessão pertence ao usuário autenticado
    - Rejeita se sessão expirada ou inexistente
    
    MOTIVO:
    Ações sensíveis (troca de senha, exclusão de conta) exigem
    prova de presença forte além do JWT. O handshake PQC garante
    que o usuário executou criptografia pós-quântica recentemente,
    protegendo contra tokens JWT roubados.
    """
    if not pqc_session_manager.validate_session(x_pqc_session, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Valid PQC session required for this operation. "
                   "Please complete PQC handshake: POST /api/v1/pqc/handshake/init",
        )
    return current_user


# Type annotation para rotas que exigem PQC
PQCSecuredUser = Annotated[User, Depends(validate_pqc_session)]
