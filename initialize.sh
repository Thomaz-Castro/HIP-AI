#!/bin/bash
 
# Move para o diretório onde o script está localizado para garantir
# que todos os caminhos relativos (.venv, .env, docker-compose.yml etc.) funcionem.
cd "$(dirname "$0")"

# Limpa a tela
clear

echo "========================================"
echo "  Sistema Medico - Iniciando..."
echo "========================================"
echo ""

# --- 1. VERIFICACAO DO PYTHON ---
echo "[INFO] Verificando se o Python 3 está instalado..."
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não foi encontrado no sistema!"
    echo "[INFO] Para instalar, use o gerenciador de pacotes da sua distribuição."
    echo "[INFO] Ex: 'sudo apt install python3' (Debian/Ubuntu) ou 'sudo dnf install python3' (Fedora)."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Python 3 encontrado."
echo ""


# --- 2 & 3. VERIFICAÇÃO E VALIDAÇÃO DO .ENV ---
echo "[INFO] Verificando arquivo de configuração (.env)..."
if [ ! -f ".env" ]; then
    echo "[AVISO] O arquivo .env não foi encontrado! Criando a partir de .env.example..."
    # Garante que .env.example exista antes de copiar
    if [ ! -f ".env.example" ]; then
        echo "[ERRO] O arquivo .env.example também não foi encontrado!"
        echo "[INFO] Não é possível continuar sem um arquivo de configuração de exemplo."
        read -p "Pressione [Enter] para sair..."
        exit 1
    fi
    cp .env.example .env
    echo "[OK] Arquivo .env criado."
    echo "[AVISO] O script será encerrado. Configure suas credenciais no arquivo .env e execute novamente."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Arquivo .env encontrado."
echo ""

echo "[INFO] Verificando credenciais no .env..."
# --- MELHORIA: Verifica também as variáveis do Postgres ---
if grep -qE "^GEMINI_API_KEY=$" ".env" || \
   grep -qE "^POSTGRES_USER=$" ".env" || \
   grep -qE "^POSTGRES_PASSWORD=$" ".env" || \
   grep -qE "^POSTGRES_DB=$" ".env"; then
    
    echo "[ERRO] Variáveis essenciais não configuradas no arquivo .env."
    echo "[INFO] Por favor, abra o .env e configure no mínimo:"
    echo "       - GEMINI_API_KEY"
    echo "       - POSTGRES_USER"
    echo "       - POSTGRES_PASSWORD"
    echo "       - POSTGRES_DB"
    echo "[INFO] Esses campos não podem ficar vazios."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Credenciais de segurança parecem estar preenchidas."
echo ""


# --- 4. AMBIENTE VIRTUAL E DEPENDÊNCIAS PYTHON ---
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Ambiente virtual não encontrado. Criando..."
    python3 -m venv "$VENV_DIR"
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "[ERRO CRÍTICO] Falha ao criar o ambiente virtual!"
    echo "[CAUSA] O pacote 'python3-venv' provavelmente não está instalado."
    install_cmd=""
    if command -v apt &> /dev/null; then install_cmd="sudo apt update && sudo apt install -y python3-venv"; fi
    if command -v dnf &> /dev/null; then install_cmd="sudo dnf install -y python3-venv"; fi
    if [ -n "$install_cmd" ]; then
        read -p "Deseja que o script tente instalar o pacote automaticamente? (s/n): " choice
        if [[ "$choice" =~ ^[sS]$ ]]; then
            echo "[INFO] Tentando instalar... Você precisará digitar sua senha de administrador."
            eval $install_cmd
            if [ $? -eq 0 ]; then echo "[OK] Pacote instalado! Execute o script novamente."; else echo "[ERRO] Instalação falhou. Instale 'python3-venv' manualmente."; fi
        else
            echo "[INFO] Instalação cancelada. Instale 'python3-venv' manualmente.";
        fi
    fi
    read -p "Pressione [Enter] para sair..."
    exit 1
fi

echo "[INFO] Ativando ambiente virtual..."
source "$VENV_DIR/bin/activate"

echo "[INFO] Instalando/atualizando dependências do requirements.txt..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao instalar as dependências Python. Verifique sua conexão com a internet."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Dependências Python instaladas."
echo ""

# --- 5. VERIFICAÇÃO DE DEPENDÊNCIAS DO SISTEMA GRÁFICO ---
QT_DEPS_FLAG=".qt_deps_installed"
if [ ! -f "$QT_DEPS_FLAG" ]; then
    echo "[INFO] Verificando dependências do sistema para a interface gráfica..."
    
    PKG_MANAGER=""
    PACKAGES=""
    
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        PACKAGES="libxcb-xinerama0 libxcb-randr0 libxcb-icccm4 libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-util1 libxcb-xkb1 libxkbcommon-x11-0"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        PACKAGES="libxcb-xinerama libxcb-randr xcb-util-wm xcb-util-keysyms xcb-util-image xcb-util libxkbcommon-x11"
    fi

    if [ -n "$PKG_MANAGER" ]; then
        read -p "A interface gráfica pode precisar de pacotes do sistema. Deseja verificar e instalar agora? (s/n): " choice
        if [[ "$choice" =~ ^[sS]$ ]]; then
            echo "[INFO] Instalando pacotes via $PKG_MANAGER. Pode ser necessário digitar sua senha."
            if [ "$PKG_MANAGER" == "apt" ]; then
                sudo apt update && sudo apt install -y $PACKAGES
            else
                sudo dnf install -y $PACKAGES
            fi

            if [ $? -eq 0 ]; then
                echo "[OK] Dependências gráficas instaladas com sucesso."
                touch $QT_DEPS_FLAG # Cria o arquivo para não perguntar novamente
            else
                echo "[ERRO] Falha ao instalar dependências gráficas. A aplicação pode não iniciar."
                echo "[INFO] Tente executar o comando de instalação manualmente."
                read -p "Pressione [Enter] para sair..."
                exit 1
            fi
        else
            echo "[AVISO] Instalação de dependências gráficas ignorada. A aplicação pode não funcionar."
        fi
    fi
    echo ""
fi


# --- 5.5. VERIFICAÇÃO DO DOCKER E BANCO DE DADOS (NOVO) ---
echo "[INFO] Verificando se o Docker e o Docker Compose estão instalados..."

# 1. Checa Docker
if ! command -v docker &> /dev/null; then
    echo "[ERRO] O comando 'docker' não foi encontrado no sistema!"
    echo "[INFO] Por favor, instale o Docker (ex: 'sudo apt install docker.io')."
    echo "[INFO] Lembre-se de iniciar o serviço: 'sudo systemctl start docker'"
    echo "[INFO] E adicione seu usuário ao grupo docker: 'sudo usermod -aG docker $USER' (requer re-login)"
    read -p "Pressione [Enter] para sair..."
    exit 1
fi

# 2. Encontra o comando do Compose (v1 ou v2)
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "[ERRO] 'docker-compose' (v1) ou 'docker compose' (v2) não foi encontrado!"
    echo "[INFO] Por favor, instale o Docker Compose (ex: 'sudo apt install docker-compose')."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Docker e '$COMPOSE_CMD' encontrados."
echo ""

# 3. Verifica o status do container
CONTAINER_NAME="hip-ai" # Definido no seu docker-compose.yml

echo "[INFO] Verificando status do container do banco de dados: $CONTAINER_NAME"

# Verifica se o container com nome exato (^) e ($) está com status "running"
if docker ps -f "name=^/${CONTAINER_NAME}$" -f "status=running" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "[OK] O container '$CONTAINER_NAME' já está em execução."
else
    echo "[AVISO] Container '$CONTAINER_NAME' não está em execução."
    echo "[INFO] Tentando iniciar o banco de dados com '$COMPOSE_CMD up -d'..."
    
    # Verifica se o docker-compose.yml existe
    if [ ! -f "docker-compose.yml" ]; then
        echo "[ERRO] Arquivo 'docker-compose.yml' não encontrado neste diretório!"
        read -p "Pressione [Enter] para sair..."
        exit 1
    fi

    # Executa o docker-compose. Ele lerá o .env automaticamente.
    $COMPOSE_CMD up -d
    
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao executar '$COMPOSE_CMD up -d'!"
        echo "[INFO] Verifique se o serviço Docker está rodando ('sudo systemctl status docker')."
        echo "[INFO] Verifique se você tem permissão ('sudo usermod -aG docker $USER')."
        echo "[INFO] Verifique os logs do Docker para mais detalhes."
        read -p "Pressione [Enter] para sair..."
        exit 1
    fi
    
    echo "[INFO] Aguardando o banco de dados (Postgres) inicializar..."
    sleep 8 # Dá um tempo (8s) para o Postgres ficar pronto para conexões
    
    # Verificação final
    if docker ps -f "name=^/${CONTAINER_NAME}$" -f "status=running" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "[OK] Container '$CONTAINER_NAME' iniciado com sucesso!"
    else
        echo "[ERRO] O container '$CONTAINER_NAME' falhou ao iniciar após o comando. Verifique os logs."
        echo "[INFO] Tente: 'docker logs $CONTAINER_NAME' ou '$COMPOSE_CMD logs db'"
        read -p "Pressione [Enter] para sair..."
        exit 1
    fi
fi
echo ""


# --- 6. EXECUCAO DO SISTEMA ---
echo "========================================"
echo "[INFO] Iniciando aplicação principal..."
echo ""
python3 medical_system.py

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[ERRO] Ocorreu um erro durante a execução do sistema!"
else
    echo "[OK] Sistema finalizado com sucesso."
fi

echo ""
read -p "Pressione [Enter] para sair..."
deactivate > /dev/null 2>&1