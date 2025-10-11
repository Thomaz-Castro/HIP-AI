@echo off
REM Define a pagina de codigo para UTF-8 para exibir acentos corretamente
chcp 65001 >nul

cls
echo ========================================
echo  Sistema Medico - Iniciando...
echo ========================================
echo.

REM --- 1. VERIFICACAO DO PYTHON ---
echo [INFO] Verificando se o Python esta instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no sistema!
    echo [INFO] Para instalar, acesse: https://www.python.org/downloads/
    echo [INFO] Lembre-se de marcar a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)
echo [OK] Python encontrado.
echo.

REM --- 2. VERIFICACAO DO ARQUIVO .ENV ---
echo [INFO] Verificando arquivo de configuracao (.env)...
if exist ".env" (
    echo [OK] Arquivo .env encontrado.
    goto :check_env_content
)

echo [AVISO] O arquivo .env nao foi encontrado!
echo [INFO] Este arquivo e essencial para a conexao com o banco de dados.
echo.

:ask_create_env
set "user_choice="
set /p "user_choice=Deseja criar um .env a partir do .env.example agora? (s/n): "

if /i "%user_choice%"=="s" (
    copy .env.example .env >nul
    echo [OK] Arquivo .env criado com sucesso!
    echo [INFO] O arquivo sera aberto para voce inserir suas credenciais.
    notepad .env
    echo [AVISO] O script sera encerrado. Configure o .env e execute novamente.
    pause
    exit /b 1
)
if /i "%user_choice%"=="n" (
    echo [INFO] Criacao do .env ignorada. O script nao pode continuar.
    pause
    exit /b 1
)

echo [ERRO] Opcao invalida. Por favor, digite apenas 's' ou 'n'.
goto :ask_create_env


:check_env_content
REM --- 3. VALIDACAO DO CONTEUDO DO .ENV ---
echo [INFO] Verificando credenciais no .env...

REM Verifica se as credenciais padrao do MongoDB foram alteradas
findstr /c:"mongodb+srv://username:password@cluster.mongodb.net/medical_system?retryWrites=true&w=majority" ".env" >nul
if %errorlevel% equ 0 (
    echo [ERRO] Suas credenciais do MongoDB no .env ainda sao as padroes.
    echo [INFO] Abra o arquivo .env e substitua a URI pelos seus dados reais.
    pause
    exit /b 1
)

REM Verifica se a GEMINI_API_KEY existe (aviso, nao erro)
findstr /r /c:"^GEMINI_API_KEY=.*[A-Za-z0-9]" ".env" >nul
if %errorlevel% neq 0 (
    echo [AVISO] A variavel 'GEMINI_API_KEY' nao foi encontrada ou esta vazia no .env.
    echo [INFO] Abra o arquivo .env e configure-a corretamente.
    pause
    exit /b 1
)
echo [OK] Conteudo do .env parece valido.
echo.

REM --- 4. AMBIENTE VIRTUAL E DEPENDENCIAS ---
if not exist ".venv\" (
    echo [INFO] Ambiente virtual nao encontrado. Criando .venv...
    python -m venv .venv
)

echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [INFO] Instalando/atualizando dependencias do requirements.txt...
pip install -r requirements.txt
echo [OK] Dependencias instaladas.
echo.


REM --- 5. EXECUCAO DO SISTEMA ---
echo ========================================
echo [INFO] Iniciando aplicacao principal...
echo.
python medical_system.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um erro durante a execucao do sistema!
    echo [INFO] Verifique as mensagens de erro acima.
    echo [INFO] Causas comuns: credenciais do .env incorretas ou falta de conexao com a internet.
) else (
    echo [OK] Sistema finalizado com sucesso.
)

echo.
pause