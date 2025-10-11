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

1. **Verifica o Python** — Confirma se o Python está instalado.
2. **Cria o ambiente virtual** — Gera uma pasta `.venv` isolada.
3. **Ativa o ambiente** — Garante que os próximos comandos usem esse ambiente.
4. **Instala dependências** — Lê o `requirements.txt` e instala tudo.
5. **Inicia o sistema** — Executa automaticamente o `medical_system.py`.

---

## ⚙️ Pré-requisitos

1. **Python:** Tenha o [Python 3.8+](https://www.python.org/downloads/) instalado.
2. **Clonar o repositório:**

   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd HIP-AI
   ```

---

## 🔑 Configuração Manual (Opcional)

Caso prefira configurar manualmente:

1. Localize o arquivo `.env.example`.
2. Faça uma cópia e renomeie para `.env`.
3. Edite o arquivo `.env` com suas credenciais:

```dotenv
# .env

# Substitua pela sua string de conexão real do MongoDB Atlas
MONGO_URI="mongodb+srv://seu_usuario:sua_senha@seu_cluster..."

# Substitua pela sua chave de API do Google Gemini
GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
```

---

## 🧠 Observação

Após a configuração inicial, sempre que quiser iniciar o sistema, basta rodar novamente o script correspondente (`initialize.bat` ou `initialize.sh`) — ele cuidará de tudo automaticamente.
