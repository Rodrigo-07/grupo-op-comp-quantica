import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class PQCKEMAlgorithm(SQLModel):
    name: str
    claimed_nist_level: int
    is_classical_secured: bool
    length_public_key: int
    length_secret_key: int
    length_ciphertext: int
    length_shared_secret: int


class PQCKEMAlgorithms(SQLModel):
    data: list[PQCKEMAlgorithm]


# Modelos para o handshake PQC em duas etapas
class PQCHandshakeInitRequest(SQLModel):
    """Requisição para iniciar handshake PQC."""
    algorithm: str | None = None


class PQCHandshakeInitResponse(SQLModel):
    """Resposta da primeira etapa: servidor gera chaves e retorna chave pública."""
    handshake_id: str
    algorithm: str
    public_key: str  # Base64 encoded
    expires_at: str  # ISO format timestamp


class PQCHandshakeCompleteRequest(SQLModel):
    """Cliente envia o ciphertext após encapsular o segredo."""
    handshake_id: str
    ciphertext: str  # Base64 encoded


class PQCHandshakeCompleteResponse(SQLModel):
    """Sessão PQC criada com sucesso."""
    session_id: str
    expires_at: str  # ISO format timestamp
    message: str


# Modelo de demonstração (apenas para testes/debug - NÃO usar em produção)
class PQCKEMHandshakeRequest(SQLModel):
    """Requisição de handshake completo (demo apenas)."""
    algorithm: str | None = None


class PQCKEMHandshakeResponse(SQLModel):
    """Resposta do handshake completo (demo apenas) - mostra ambos os segredos."""
    algorithm: str
    public_key: str
    ciphertext: str
    server_shared_secret: str
    client_shared_secret: str
    shared_secret_match: bool
    details: PQCKEMAlgorithm
