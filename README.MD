# HIP-AI: Guia de Instalação

Guia rápido para configurar e executar o projeto em sua máquina local.

## 🚀 Instalação Automática

O projeto possui scripts de inicialização (`initialize.bat` e `initialize.sh`) que **automatizam todo o processo de instalação e execução**.
Você só precisa rodar **um único comando** para tudo funcionar.

### ▶️ Execução Rápida

Escolha o comando conforme o seu sistema operacional e execute **dentro da pasta do projeto**:

#### **Windows**

```cmd
.\initialize.bat
```

#### **Linux / macOS**

Primeiro, conceda permissão de execução (somente na primeira vez):

```bash
chmod +x initialize.sh
```

Depois, execute:

```bash
./initialize.sh
```

### 💡 O que o script faz automaticamente

1. **Verifica o Python** — Confirma se o Python 3.10, 3.11, 3.12 ou 3.13 está instalado e seleciona uma versão compatível.
2. **Verifica o arquivo `.env`** — Confirma se o arquivo de configuração existe e se as credenciais estão preenchidas.
3. **Cria o ambiente virtual** — Gera uma pasta `.venv` isolada (se ainda não existir).
4. **Ativa o ambiente** — Garante que os próximos comandos usem esse ambiente.
5. **Instala/atualiza dependências** — Lê o arquivo de requisitos e instala todos os pacotes necessários.
6. **Verifica o Docker** — Confirma se o Docker e Docker Compose estão instalados.
7. **Inicia o banco de dados** — Sobe o container PostgreSQL automaticamente via Docker Compose.
8. **Inicia o sistema** — Executa automaticamente o `medical_system.py`.

---

## ⚙️ Pré-requisitos

### 1. **Python**
- **Versões compatíveis:** Python 3.10, 3.11, 3.12 ou 3.13
- **Python 3.14+** ainda não é compatível com as bibliotecas necessárias
- [Download Python 3.12 (recomendado)](https://www.python.org/downloads/release/python-3120/)
- ⚠️ **Importante:** Durante a instalação, marque a opção **"Add Python to PATH"**

### 2. **Docker Desktop (para windows, para linux docker normal)**
- Necessário para executar o banco de dados PostgreSQL
- [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- ⚠️ **Importante:** Certifique-se de que o Docker Desktop está **aberto e em execução** antes de rodar o script

### 3. **Clonar o repositório**

```bash
git clone https://github.com/Thomaz-Castro/HIP-AI
cd HIP-AI
```

---

## 🔑 Configuração do Arquivo `.env`

### Configuração Automática (Recomendada)

Na primeira execução, o script detectará automaticamente se o arquivo `.env` não existe e oferecerá criar um a partir do `.env.example`. Basta:

1. Responder **`s`** (sim) quando perguntado
2. O arquivo será criado e aberto automaticamente no Bloco de Notas
3. Preencher as credenciais necessárias
4. Salvar e executar o script novamente

### Configuração Manual (Opcional)

Caso prefira configurar manualmente:

1. Localize o arquivo `.env.example`
2. Faça uma cópia e renomeie para `.env`
3. Edite o arquivo `.env` com suas credenciais:

```dotenv
# ==================================
# API DO GOOGLE GEMINI
# ==================================
GEMINI_API_KEY=sua_chave_aqui

# ==================================
# CONFIGURAÇÃO DO POSTGRESQL
# ==================================
POSTGRES_DB=medical_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_segura

# ----------------------------------
# Variáveis de Conexão da Aplicação
# ----------------------------------
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ----------------------------------
# Chave de Encriptação
# ----------------------------------
ENCRYPTION_KEY=sua_chave_de_encriptacao
```

⚠️ **Campos obrigatórios:**
- `GEMINI_API_KEY` — Sua chave da API do Google Gemini
- `ENCRYPTION_KEY` — Chave para criptografia de dados sensíveis
- `POSTGRES_USER` — Usuário do banco de dados
- `POSTGRES_PASSWORD` — Senha do banco de dados
- `POSTGRES_DB` — Nome do banco de dados

---

## 🐳 Sobre o Docker

O script gerencia automaticamente o container do PostgreSQL:

- **Nome do container:** `hip-ai`
- **Arquivo de configuração:** `docker-compose.yml`
- Se o container não estiver rodando, o script iniciará automaticamente
- Se já estiver rodando, o script prosseguirá normalmente

### Comandos úteis do Docker (manual):

```bash
# Ver containers em execução
docker ps

# Ver logs do banco de dados
docker logs hip-ai

# Parar o container
docker-compose down

# Iniciar o container manualmente
docker-compose up -d
```

---

## 📦 Dependências Instaladas

O script instala automaticamente os seguintes pacotes:

- `PyQt5==5.15.9` — Interface gráfica
- `psycopg2-binary==2.9.11` — Conexão com PostgreSQL
- `protobuf==4.25.3` — Protocolo de serialização
- `google-generativeai==0.8.3` — API do Google Gemini
- `cryptography==41.0.5` — Criptografia de dados
- `python-dotenv==1.0.0` — Gerenciamento de variáveis de ambiente
- `reportlab==4.4.5` — Geração de relatórios PDF

---

## 🔧 Solução de Problemas

### Erro: "Python não foi encontrado"
- Verifique se o Python está instalado corretamente
- Confirme que marcou "Add Python to PATH" durante a instalação
- Tente executar `python --version` no terminal

### Erro: "Docker não foi encontrado"
- Certifique-se de que o Docker Desktop está instalado
- Verifique se o Docker Desktop está **aberto e em execução**
- Procure o ícone da baleia na bandeja do sistema

### Erro: "Falha ao criar ambiente virtual"
- Execute o comando manualmente: `python -m venv .venv`
- Tente executar o script como Administrador (Windows)

### Erro: "Container falhou ao iniciar"
- Verifique os logs: `docker logs hip-ai`
- Certifique-se de que a porta 5432 não está sendo usada por outro serviço
- Tente reiniciar o Docker Desktop

### Erro: "Variáveis essenciais não configuradas"
- Abra o arquivo `.env` e preencha todos os campos obrigatórios
- Certifique-se de que nenhum campo está vazio (sem valor após o `=`)

---

## 🧠 Observação

Após a configuração inicial, sempre que quiser iniciar o sistema, basta rodar novamente o script correspondente (`initialize.bat` ou `initialize.sh`) — ele cuidará de verificar tudo e iniciar o sistema automaticamente.

---

## 📝 Estrutura do Projeto

```
HIP-AI/
├── .env                    # Configurações (não versionado)
├── .env.example           # Exemplo de configurações
├── docker-compose.yml     # Configuração do PostgreSQL
├── initialize.bat         # Script de inicialização (Windows)
├── initialize.sh          # Script de inicialização (Linux/macOS)
├── medical_system.py      # Aplicação principal
├── pip-requirements       # Lista de dependências
└── .venv/                 # Ambiente virtual (criado automaticamente)
```
