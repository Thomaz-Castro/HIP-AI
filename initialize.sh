#!/bin/bash

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

# --- 2. VERIFICACAO DO ARQUIVO .ENV ---
echo "[INFO] Verificando arquivo de configuração (.env)..."
if [ -f ".env" ]; then
    echo "[OK] Arquivo .env encontrado."
else
    echo "[AVISO] O arquivo .env não foi encontrado!"
    echo "[INFO] Este arquivo é essencial para a conexão com o banco de dados."
    echo ""

    # Loop para perguntar ao usuário se deseja criar o .env
    while true; do
        read -p "Deseja criar um .env a partir do .env.example agora? (s/n): " user_choice
        case $user_choice in
            [Ss]* )
                cp .env.example .env
                echo "[OK] Arquivo .env criado com sucesso!"
                echo "[AVISO] O script será encerrado. Abra o arquivo '.env' com um editor de texto,"
                echo "        configure suas credenciais e execute o script novamente."
                read -p "Pressione [Enter] para sair..."
                exit 1
                ;;
            [Nn]* )
                echo "[INFO] Criação do .env ignorada. O script não pode continuar."
                read -p "Pressione [Enter] para sair..."
                exit 1
                ;;
            * )
                echo "[ERRO] Opção inválida. Por favor, digite apenas 's' ou 'n'."
                ;;
        esac
    done
fi
echo ""

# --- 3. VALIDACAO DO CONTEUDO DO .ENV ---
echo "[INFO] Verificando credenciais no .env..."

# Verifica se as credenciais padrão do MongoDB foram alteradas
if grep -q "mongodb+srv://username:password@cluster.mongodb.net/medical_system?retryWrites=true&w=majority" ".env"; then
    echo "[ERRO] Suas credenciais do MongoDB no .env ainda são as padrões."
    echo "[INFO] Abra o arquivo .env e substitua a URI pelos seus dados reais."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi

# Verifica se a GEMINI_API_KEY existe e não está vazia
if ! grep -qE "^GEMINI_API_KEY=.*[A-Za-z0-9]" ".env"; then
    echo "[AVISO] A variável 'GEMINI_API_KEY' não foi encontrada ou está vazia no .env."
    echo "[INFO] Abra o arquivo .env e configure-a corretamente."
    read -p "Pressione [Enter] para sair..."
    exit 1
fi
echo "[OK] Conteúdo do .env parece válido."
echo ""

# --- 4. AMBIENTE VIRTUAL E DEPENDENCIAS ---
if [ ! -d ".venv" ]; then
    echo "[INFO] Ambiente virtual não encontrado. Criando .venv..."
    python3 -m venv .venv
fi

echo "[INFO] Ativando ambiente virtual..."
source .venv/bin/activate

echo "[INFO] Instalando/atualizando dependências do requirements.txt..."
pip install -r requirements.txt
echo "[OK] Dependências instaladas."
echo ""

# --- 5. EXECUCAO DO SISTEMA ---
echo "========================================"
echo "[INFO] Iniciando aplicação principal..."
echo ""
python3 medical_system.py

# Captura o código de saída do script python
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[ERRO] Ocorreu um erro durante a execução do sistema!"
    echo "[INFO] Verifique as mensagens de erro acima."
    echo "[INFO] Causas comuns: credenciais do .env incorretas ou falta de conexão com a internet."
else
    echo "[OK] Sistema finalizado com sucesso."
fi

echo ""
read -p "Pressione [Enter] para sair..."

# Desativa o ambiente virtual ao sair (boa prática)
deactivate