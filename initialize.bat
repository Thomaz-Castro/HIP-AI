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
    REM Verifica se o .env.example existe antes de copiar
    if not exist ".env.example" (
        echo [ERRO] O arquivo .env.example tambem nao foi encontrado!
        echo [INFO] Nao e possivel continuar sem um arquivo de configuracao de exemplo.
        pause
        exit /b 1
    )
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

REM Verifica se alguma das chaves essenciais esta vazia (termina com =)
(
    findstr /R /C:"^GEMINI_API_KEY=$" ".env" >nul || ^
    findstr /R /C:"^POSTGRES_USER=$" ".env" >nul || ^
    findstr /R /C:"^POSTGRES_PASSWORD=$" ".env" >nul || ^
    findstr /R /C:"^POSTGRES_DB=$" ".env" >nul
)
if %errorlevel% equ 0 (
    echo [ERRO] Variaveis essenciais nao configuradas no arquivo .env.
    echo [INFO] Por favor, abra o .env e configure no minimo:
    echo        - GEMINI_API_KEY
    echo        - POSTGRES_USER
    echo        - POSTGRES_PASSWORD
    echo        - POSTGRES_DB
    echo [INFO] Esses campos nao podem ficar vazios.
    pause
    exit /b 1
)
echo [OK] Credenciais de seguranca parecem estar preenchidas.
echo.

REM --- 4. AMBIENTE VIRTUAL E DEPENDENCIAS ---
if not exist ".venv\" (
    echo [INFO] Ambiente virtual nao encontrado. Criando .venv...
    python -m venv .venv
)

echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [INFO] Instalando/atualizando dependencias do requirements.txt...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar as dependencias Python.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

REM --- 5. VERIFICACAO DO DOCKER E BANCO DE DADOS ---
echo [INFO] Verificando se o Docker esta em execucao...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O comando 'docker' nao foi encontrado!
    echo [INFO] Por favor, inicie o Docker Desktop.
    pause
    exit /b 1
)

REM Encontra o comando do Compose (v1 ou v2)
set "COMPOSE_CMD="
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set "COMPOSE_CMD=docker-compose"
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set "COMPOSE_CMD=docker compose"
    )
)

if not defined COMPOSE_CMD (
    echo [ERRO] 'docker-compose' (v1) ou 'docker compose' (v2) nao foi encontrado!
    echo [INFO] Verifique sua instalacao do Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker e '%COMPOSE_CMD%' encontrados.
echo.

REM 3. Verifica o status do container
set "CONTAINER_NAME=hip-ai"
echo [INFO] Verificando status do container do banco de dados: %CONTAINER_NAME%

docker ps -f "name=^/%CONTAINER_NAME%$" -f "status=running" --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" >nul
if %errorlevel% equ 0 (
    echo [OK] O container '%CONTAINER_NAME%' ja esta em execucao.
    goto :run_app
)

echo [AVISO] Container '%CONTAINER_NAME%' nao esta em execucao.
echo [INFO] Tentando iniciar o banco de dados com '%COMPOSE_CMD% up -d'...

if not exist "docker-compose.yml" (
    echo [ERRO] Arquivo 'docker-compose.yml' nao encontrado neste diretorio!
    pause
    exit /b 1
)

REM Executa o docker-compose. Ele lera o .env automaticamente.
%COMPOSE_CMD% up -d
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao executar '%COMPOSE_CMD% up -d'!
    echo [INFO] Verifique se o Docker Desktop esta realmente em execucao.
    pause
    exit /b 1
)

echo [INFO] Aguardando o banco de dados (Postgres) inicializar...
timeout /t 8 /nobreak >nul

REM Verificacao final
docker ps -f "name=^/%CONTAINER_NAME%$" -f "status=running" --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" >nul
if %errorlevel% equ 0 (
    echo [OK] Container '%CONTAINER_NAME%' iniciado com sucesso!
) else (
    echo [ERRO] O container '%CONTAINER_NAME%' falhou ao iniciar. Verifique os logs.
    echo [INFO] Tente: 'docker logs %CONTAINER_NAME%' ou '%COMPOSE_CMD% logs db'
    pause
    exit /b 1
)
echo.


REM --- 6. EXECUCAO DO SISTEMA ---
:run_app
echo ========================================
echo [INFO] Iniciando aplicacao principal...
echo.
python medical_system.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um erro durante a execucao do sistema!
    echo [INFO] Verifique as mensagens de erro acima.
) else (
    echo [OK] Sistema finalizado com sucesso.
)

echo.
pause