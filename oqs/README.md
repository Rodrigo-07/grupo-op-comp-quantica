# 🔐 Implementação de Criptografia Pós-Quântica (PQC) com Open Quantum Safe

> **Autenticação resistente a computadores quânticos usando liboqs e FastAPI**

[![Open Quantum Safe](https://img.shields.io/badge/OQS-liboqs-blue)](https://openquantumsafe.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)](https://www.docker.com/)
[![Kyber](https://img.shields.io/badge/NIST-Kyber-purple)](https://pq-crystals.org/kyber/)

---

## 📚 Índice

- [Visão Geral](#-visão-geral)
- [Motivação](#-motivação)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Funciona](#-como-funciona)
- [Início Rápido](#-início-rápido)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Equipe](#-equipe)
- [Referências](#-referências)

---

## 🎯 Visão Geral

Este projeto implementa um **sistema de autenticação híbrido** que combina:

- **Autenticação clássica** (JWT) para controle de acesso tradicional
- **Autenticação pós-quântica** (PQC) usando algoritmos KEM para operações críticas

O objetivo é proteger operações sensíveis contra **ataques de computadores quânticos futuros**, implementando criptografia resistente a quânticos no nível da aplicação usando a biblioteca **liboqs (Open Quantum Safe)**.

### 🔑 Características Principais

✅ **Autenticação Híbrida**: JWT tradicional + Sessões PQC
✅ **Algoritmos NIST**: Kyber512/768/1024 (KEM)
✅ **Step-up Security**: PQC apenas quando necessário
✅ **Docker Ready**: Ambiente completo containerizado
✅ **API REST**: Endpoints FastAPI documentados
✅ **Cliente Demo**: Script Python de demonstração completo

---

## 🌟 Motivação

### Por que Criptografia Pós-Quântica?

Computadores quânticos representam uma ameaça futura para os sistemas criptográficos atuais:

| Algoritmo Clássico | Vulnerabilidade Quântica | Alternativa PQC |
|-------------------|--------------------------|-----------------|
| RSA | ❌ Quebrado pelo Algoritmo de Shor | ✅ Kyber (KEM) |
| ECC | ❌ Quebrado pelo Algoritmo de Shor | ✅ Dilithium (Assinaturas) |
| DH | ❌ Vulnerável | ✅ KEMs pós-quânticos |

### Cenário de Ameaça

```
┌─────────────────────┐
│ Adversário captura  │
│ tráfego hoje        │ ──┐
└─────────────────────┘   │
                          │ "Harvest Now, Decrypt Later"
┌─────────────────────┐   │
│ Computador quântico │   │
│ no futuro          │ ◄─┘
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Dados comprometidos │
└─────────────────────┘
```

**Nossa solução**: Implementar PQC **agora** para proteger dados sensíveis a longo prazo.

---

## 🏗️ Arquitetura

### Modelo Híbrido de Autenticação

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENTE                                │
├──────────────────────────────────────────────────────────┤
│  1. Login (email/senha) ────────────► JWT Token          │
│                                                            │
│  2. Handshake PQC Init ─────────────► Chave Pública KEM  │
│                                                            │
│  3. Encapsular Segredo (local) ─────► Ciphertext         │
│                                                            │
│  4. Handshake Complete ─────────────► Session ID         │
│                                                            │
│  5. Operação Crítica:                                     │
│     Headers: Authorization + X-PQC-Session                │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                    SERVIDOR                               │
├──────────────────────────────────────────────────────────┤
│  ✓ Valida JWT (identidade)                               │
│  ✓ Valida Sessão PQC (prova criptográfica recente)       │
│  ✓ Executa operação sensível                             │
└──────────────────────────────────────────────────────────┘
```

### Camadas de Segurança

1. **JWT (Autenticação Clássica)**
   - Identifica o usuário
   - Controle de acesso básico
   - Tempo de vida: 8 dias

2. **Sessão PQC (Step-up Security)**
   - Prova de presença criptográfica forte
   - Requerida apenas para operações críticas
   - Tempo de vida: 5 minutos
   - Baseada em KEM resistente a quânticos

---

## 📁 Estrutura do Projeto

```
oqs/
├── README.md                          # 👈 Você está aqui
│
├── pqc-fastapi-implementation/        # Implementação principal
│   ├── backend/                       # API FastAPI com PQC
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── routes/
│   │   │   │   │   ├── pqc.py        # 🔐 Endpoints PQC
│   │   │   │   │   └── users.py      # Rotas protegidas
│   │   │   │   └── deps.py           # Dependency: validate_pqc_session
│   │   │   ├── services/
│   │   │   │   └── pqc.py            # 🔑 Serviço KEM (liboqs)
│   │   │   ├── core/
│   │   │   │   ├── pqc_sessions.py   # Gerenciador de sessões
│   │   │   │   └── config.py         # Configurações PQC
│   │   │   └── models.py             # Schemas Pydantic
│   │   ├── Dockerfile                # 🐳 Build com liboqs
│   │   └── pyproject.toml            # Dependência: liboqs-python
│   │
│   ├── frontend/                      # Interface React (opcional)
│   │
│   ├── docs/                          # 📖 Documentação técnica
│   │   ├── PQC_INTEGRATION.md        # Guia de integração
│   │   ├── ARCHITECTURE.md           # Arquitetura detalhada
│   │   └── QUICK_START.md            # Tutorial rápido
│   │
│   ├── examples/                      # 💡 Exemplos práticos
│   │   └── pqc_client_demo.py        # Cliente Python completo
│   │
│   ├── docker-compose.yml             # Orquestração de serviços
│   └── README.md                      # Documentação do projeto
│
└── .gitignore
```

### Componentes-Chave

| Componente | Responsabilidade | Tecnologia |
|------------|------------------|------------|
| **PQCService** | Wrapper para liboqs (KEM) | Python + oqs |
| **PQCSessionManager** | Gerenciador de sessões | In-memory (Redis ready) |
| **validate_pqc_session** | Dependency FastAPI | Header validation |
| **Docker Image** | Build liboqs + app | Multi-stage Dockerfile |
| **API Endpoints** | REST API para PQC | FastAPI routes |

---

## 🔄 Como Funciona

### Fluxo Completo de Autenticação

#### 1️⃣ Login Tradicional (JWT)

```http
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=senha123
```

**Resposta**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 2️⃣ Descoberta de Algoritmos (Opcional)

```http
GET /api/v1/pqc/kems
```

**Resposta**:
```json
{
  "data": [
    {
      "name": "Kyber512",
      "claimed_nist_level": 1,
      "is_classical_secured": true,
      "length_public_key": 800,
      "length_secret_key": 1632,
      "length_ciphertext": 768,
      "length_shared_secret": 32
    }
  ]
}
```

#### 3️⃣ Handshake PQC - Inicialização

```http
POST /api/v1/pqc/handshake/init
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "algorithm": "Kyber512"
}
```

**Resposta**:
```json
{
  "handshake_id": "abc123...",
  "algorithm": "Kyber512",
  "public_key": "BASE64_ENCODED_PUBLIC_KEY",
  "expires_at": "2024-01-15T10:30:00Z"
}
```

#### 4️⃣ Cliente Encapsula Segredo (Local)

```python
import oqs
import base64

# Decodifica chave pública
public_key = base64.b64decode(response['public_key'])

# Encapsula segredo com liboqs
with oqs.KeyEncapsulation('Kyber512') as client:
    ciphertext, shared_secret = client.encap_secret(public_key)

# Envia ciphertext ao servidor
ciphertext_b64 = base64.b64encode(ciphertext).decode()
```

#### 5️⃣ Handshake PQC - Completar

```http
POST /api/v1/pqc/handshake/complete
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "handshake_id": "abc123...",
  "ciphertext": "BASE64_ENCODED_CIPHERTEXT"
}
```

**Resposta**:
```json
{
  "session_id": "xyz789...",
  "expires_at": "2024-01-15T10:35:00Z",
  "message": "PQC session established successfully"
}
```

#### 6️⃣ Operação Protegida

```http
PATCH /api/v1/users/me/password
Authorization: Bearer eyJhbGc...
X-PQC-Session: xyz789...
Content-Type: application/json

{
  "current_password": "senha123",
  "new_password": "novaSenha456"
}
```

**Resposta**:
```json
{
  "message": "Password updated successfully"
}
```

### Fluxo sem Sessão PQC (❌ Falha)

```http
PATCH /api/v1/users/me/password
Authorization: Bearer eyJhbGc...
# ❌ Faltando: X-PQC-Session

HTTP/1.1 403 Forbidden
{
  "detail": "Valid PQC session required for this operation.
             Please complete PQC handshake: POST /api/v1/pqc/handshake/init"
}
```

---

## 🚀 Início Rápido

### Pré-requisitos

- Docker & Docker Compose
- Python 3.10+ (para cliente demo)
- Git

### 1. Clone o Repositório

```bash
git clone https://github.com/Op-Quantum-Computing/grupo-op-comp-quantica.git
cd grupo-op-comp-quantica/oqs/pqc-fastapi-implementation
```

### 2. Configure Variáveis de Ambiente

```bash
cp .env.example .env
# Edite .env com suas configurações
```

### 3. Inicie os Serviços

```bash
docker-compose up -d
```

Aguarde o build do liboqs (primeira vez leva ~5 minutos).

### 4. Verifique os Serviços

```bash
# API Backend
curl http://localhost:8000/api/v1/utils/health-check/

# Documentação interativa
open http://localhost:8000/docs
```

### 5. Execute o Cliente Demo

```bash
# Instale liboqs localmente
pip install liboqs-python

# Execute o demo
cd examples
python pqc_client_demo.py
```

**Saída esperada**:
```
============================================================
  DEMONSTRAÇÃO: Autenticação PQC (Post-Quantum Crypto)
============================================================

📧 1. Login JWT...
✅ JWT obtido: eyJhbGciOiJIUzI1NiIsInR5cCI6...

🔐 2. Listar algoritmos PQC...
✅ 12 algoritmos disponíveis:
   - Kyber512: NIST Level 1
   - Kyber768: NIST Level 3
   ...

🤝 3. Handshake PQC (Kyber512)...
   → POST /pqc/handshake/init
   ✓ Handshake ID: abc123...
   ✓ Chave pública recebida (1088 bytes)
   → Cliente: Encapsular segredo com KEM
   ✓ Ciphertext gerado (768 bytes)
   → POST /pqc/handshake/complete
✅ Sessão PQC criada!
   Session ID: xyz789...

🔒 4. Trocar senha (operação protegida)...
✅ Operação protegida autenticada com sucesso!

⚠️  5. Testar sem sessão PQC (deve falhar)...
✅ Corretamente rejeitado! (falta X-PQC-Session)

============================================================
✅ DEMONSTRAÇÃO COMPLETA!
============================================================
```

---

## 🛠️ Tecnologias Utilizadas

### Backend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **FastAPI** | 0.115+ | Framework web moderno |
| **liboqs** | latest | Biblioteca C do OQS |
| **liboqs-python** | 0.10.0+ | Bindings Python |
| **SQLModel** | 0.0.22+ | ORM com Pydantic |
| **PostgreSQL** | 17 | Banco de dados |
| **Docker** | 20.10+ | Containerização |

### Algoritmos Criptográficos

| Categoria | Algoritmo | Status NIST | Uso |
|-----------|-----------|-------------|-----|
| **KEM** | Kyber512 | ✅ Padrão | Handshakes PQC |
| **KEM** | Kyber768 | ✅ Padrão | Alta segurança |
| **KEM** | Kyber1024 | ✅ Padrão | Máxima segurança |

### Infraestrutura Docker

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile  # Multi-stage com liboqs
    depends_on:
      - db
    environment:
      - DEFAULT_PQC_KEM=Kyber512
      - PQC_SESSION_TTL_MINUTES=5

  db:
    image: postgres:17

  frontend:
    build:
      context: ./frontend
```

---

## 📖 Documentação Adicional

### Guias Técnicos

- **[PQC_INTEGRATION.md](./pqc-fastapi-implementation/docs/PQC_INTEGRATION.md)** - Integração técnica detalhada
- **[ARCHITECTURE.md](./pqc-fastapi-implementation/docs/ARCHITECTURE.md)** - Arquitetura do sistema
- **[QUICK_START.md](./pqc-fastapi-implementation/docs/QUICK_START.md)** - Tutorial passo a passo

### APIs e Endpoints

Documentação interativa disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Exemplos de Código

Todos os exemplos estão em [`examples/`](./pqc-fastapi-implementation/examples/):
- `pqc_client_demo.py` - Cliente Python completo
- (Futuros) Exemplos em JavaScript, Go, Rust

---

## 👥 Equipe

Este projeto foi desenvolvido por:

- **Ever**
- **Gabriel Pelinsari**
- **Leandro**
- **Paula**
- **Rodrigo**

### Instituição

**Grupo de Pesquisa em Computação Quântica**
Op-Quantum-Computing

---

## 📚 Referências

### Open Quantum Safe (OQS)

- **Site oficial**: [openquantumsafe.org](https://openquantumsafe.org/)
- **GitHub liboqs**: [github.com/open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs)
- **Python bindings**: [github.com/open-quantum-safe/liboqs-python](https://github.com/open-quantum-safe/liboqs-python)

### NIST Post-Quantum Cryptography

- **NIST PQC Project**: [csrc.nist.gov/projects/post-quantum-cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- **Kyber Specification**: [pq-crystals.org/kyber](https://pq-crystals.org/kyber/)
- **Dilithium Specification**: [pq-crystals.org/dilithium](https://pq-crystals.org/dilithium/)

### Papers e Artigos

1. **"CRYSTALS-Kyber Algorithm Specifications And Supporting Documentation"**
   NIST PQC Standardization - Round 3 Submission

2. **"Post-Quantum Cryptography: Current State and Quantum Mitigation"**
   IEEE Security & Privacy, 2023

3. **"Transitioning Organizations to Post-Quantum Cryptography"**
   Nature, 2024

### Recursos de Aprendizado

- 📺 [Vídeo: Introdução à Criptografia Pós-Quântica](https://www.youtube.com/watch?v=...)
- 📖 [Tutorial: Começando com liboqs](https://github.com/open-quantum-safe/liboqs/wiki)
- 🎓 [Curso: Quantum-Safe Cryptography](https://www.coursera.org/...)

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../LICENSE) para mais detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---
