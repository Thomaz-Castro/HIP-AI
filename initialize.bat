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

REM Verificar versão do Python
echo [INFO] Verificando versao do Python...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Versao padrão encontrada: %PYTHON_VERSION%

REM Extrair versão principal (3.12, 3.13, etc)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Tentar encontrar uma versão compatível
set "PYTHON_CMD="
set "FOUND_VERSION="

echo [INFO] Procurando versao compativel de Python (3.11 ou 3.12)...

REM Tentar Python 3.12
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.12 encontrado!
    set "PYTHON_CMD=py -3.12"
    set "FOUND_VERSION=3.12"
    goto :python_ok
)

REM Tentar Python 3.11
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.11 encontrado!
    set "PYTHON_CMD=py -3.11"
    set "FOUND_VERSION=3.11"
    goto :python_ok
)

REM Tentar Python 3.10
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.10 encontrado!
    set "PYTHON_CMD=py -3.10"
    set "FOUND_VERSION=3.10"
    goto :python_ok
)

REM Verificar se a versão padrão é compatível (3.10, 3.11 ou 3.12)
if %MAJOR% equ 3 (
    if %MINOR% geq 10 if %MINOR% leq 13 (
        echo [OK] Python %PYTHON_VERSION% e compativel!
        set "PYTHON_CMD=python"
        set "FOUND_VERSION=%PYTHON_VERSION%"
        goto :python_ok
    )
)

REM Nenhuma versão compatível encontrada
echo.
echo [ERRO] Nenhuma versao compativel de Python foi encontrada!
echo [INFO] Este sistema requer Python 3.10, 3.11, 3.12 ou 3.13
echo [INFO] Python 3.14+ ainda nao e compativel com as bibliotecas necessarias.
echo.
echo [INFO] Para instalar Python 3.12 (recomendado):
echo        1. Acesse: https://www.python.org/downloads/release/python-3120/
echo        2. Baixe o instalador para Windows (64-bit)
echo        3. Durante a instalacao, MARQUE "Add Python to PATH"
echo        4. Execute este script novamente
echo.
echo [INFO] Versoes disponiveis para download:
echo        - Python 3.12: https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
echo        - Python 3.11: https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
echo.
pause
exit /b 1

:python_ok
echo [OK] Usando Python %FOUND_VERSION%
echo [INFO] Comando: %PYTHON_CMD%
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

REM Verifica se alguma das chaves essenciais esta vazia
findstr /R /C:"^GEMINI_API_KEY=$" ".env" >nul 2>&1
if %errorlevel% equ 0 goto :env_error

findstr /R /C:"^ENCRYPTION_KEY=$" ".env" >nul 2>&1
if %errorlevel% equ 0 goto :env_error

findstr /R /C:"^POSTGRES_USER=$" ".env" >nul 2>&1
if %errorlevel% equ 0 goto :env_error

findstr /R /C:"^POSTGRES_PASSWORD=$" ".env" >nul 2>&1
if %errorlevel% equ 0 goto :env_error

findstr /R /C:"^POSTGRES_DB=$" ".env" >nul 2>&1
if %errorlevel% equ 0 goto :env_error

goto :env_ok

:env_error
echo [ERRO] Variaveis essenciais nao configuradas no arquivo .env.
echo [INFO] Por favor, abra o .env e configure no minimo:
echo        - GEMINI_API_KEY
echo        - ENCRYPTION_KEY
echo        - POSTGRES_USER
echo        - POSTGRES_PASSWORD
echo        - POSTGRES_DB
echo [INFO] Esses campos nao podem ficar vazios.
pause
exit /b 1

:env_ok
echo [OK] Credenciais de seguranca parecem estar preenchidas.
echo.

REM --- 4. AMBIENTE VIRTUAL E DEPENDENCIAS ---
if not exist ".venv\" (
    echo [INFO] Ambiente virtual nao encontrado. Criando .venv...
    echo [INFO] Usando: %PYTHON_CMD%
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual!
        echo [INFO] Tente executar manualmente: %PYTHON_CMD% -m venv .venv
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado com sucesso!
)

echo [INFO] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [INFO] Verificando versao do Python no ambiente virtual...
python --version

echo [INFO] Atualizando pip...
python -m pip install --upgrade pip --quiet

echo [INFO] Instalando/atualizando dependencias do pip-requirements...
if exist "pip-requirements" (
    pip install -r pip-requirements
) else if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [AVISO] Arquivo de requisitos nao encontrado. Instalando pacotes individualmente...
)

if %errorlevel% neq 0 (
    echo [AVISO] Falha na instalacao automatica. Tentando instalar pacotes individualmente...
    pip install PyQt5==5.15.9
    pip install psycopg2-binary==2.9.11
    pip install protobuf==4.25.3
    pip install google-generativeai==0.8.3
    pip install cryptography==41.0.5
    pip install python-dotenv==1.0.0
    pip install reportlab==4.4.5
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar as dependencias Python.
        pause
        exit /b 1
    )
)
echo [OK] Dependencias instaladas.
echo.

REM --- 5. VERIFICACAO DO DOCKER E BANCO DE DADOS ---
echo [INFO] Verificando se o Docker esta instalado...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O comando 'docker' nao foi encontrado!
    echo [INFO] Instale o Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker instalado.

REM Encontra o comando do Compose (v1 ou v2)
set "COMPOSE_CMD="

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set "COMPOSE_CMD=docker-compose"
    goto :compose_found
)

docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    set "COMPOSE_CMD=docker compose"
    goto :compose_found
)

echo [ERRO] 'docker-compose' (v1) ou 'docker compose' (v2) nao foi encontrado!
echo [INFO] Verifique sua instalacao do Docker Desktop.
pause
exit /b 1

:compose_found
echo [OK] Comando '%COMPOSE_CMD%' encontrado.
echo.

REM Verifica o status do container
set "CONTAINER_NAME=hip-ai"
echo [INFO] Verificando status do container do banco de dados: %CONTAINER_NAME%

docker ps -a --filter "name=%CONTAINER_NAME%" --format "{{.Status}}" 2>nul | findstr /C:"Up" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] O container '%CONTAINER_NAME%' ja esta em execucao.
    goto :run_app
)

echo [AVISO] Container '%CONTAINER_NAME%' nao esta em execucao.
echo [INFO] Tentando iniciar o banco de dados com '%COMPOSE_CMD% up -d'...
echo [INFO] CERTIFIQUE-SE de que o Docker Desktop esta aberto!
echo.

if not exist "docker-compose.yml" (
    echo [ERRO] Arquivo 'docker-compose.yml' nao encontrado neste diretorio!
    pause
    exit /b 1
)

REM Executa o docker-compose. Ele lera o .env automaticamente.
echo [INFO] Baixando imagem do Postgres (se necessario) e iniciando container...
%COMPOSE_CMD% up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao executar '%COMPOSE_CMD% up -d'!
    echo [INFO] Certifique-se de que:
    echo        1. O Docker Desktop esta ABERTO e EM EXECUCAO
    echo        2. Voce pode ver o icone da baleia na bandeja do sistema
    echo        3. Tente executar este script como Administrador
    echo.
    pause
    exit /b 1
)

echo [INFO] Aguardando o banco de dados (Postgres) inicializar...
timeout /t 8 /nobreak >nul

REM Verificacao final
docker ps --filter "name=%CONTAINER_NAME%" --format "{{.Status}}" 2>nul | findstr /C:"Up" >nul 2>&1
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