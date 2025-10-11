#!/bin/bash

# Move para o diretório onde o script está localizado para garantir
# que todos os caminhos relativos (.venv, .env, etc.) funcionem.
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
# (O código do seu .env deve estar aqui)
echo "[INFO] Verificando arquivo de configuração (.env)..."
if [ ! -f ".env" ]; then
    echo "[AVISO] O arquivo .env não foi encontrado! Criando a partir de .env.example..."
    cp .env.example .env
    echo "[OK] Arquivo .env criado."
    echo "[AVISO] O script será encerrado. Configure suas credenciais no arquivo .env e execute novamente."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Arquivo .env encontrado."
echo ""
echo "[INFO] Verificando credenciais no .env..."
if grep -q "mongodb+srv://username:password@cluster.mongodb.net/medical_system?retryWrites=true&w=majority" ".env" || ! grep -qE "^GEMINI_API_KEY=.*[A-Za-z0-9]" ".env"; then
    echo "[ERRO] As credenciais no arquivo .env parecem ser as padrões ou estão incompletas."
    echo "[INFO] Por favor, abra o arquivo .env e configure a URI do MongoDB e a GEMINI_API_KEY."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Conteúdo do .env parece válido."
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

# --- 5. VERIFICAÇÃO DE DEPENDÊNCIAS DO SISTEMA GRÁFICO (NOVO) ---
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