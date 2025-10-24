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

REM Verifica se GEMINI_API_KEY esta vazia (ex: "GEMINI_API_KEY=")
findstr /r /c:"^GEMINI_API_KEY=$" ".env" >nul
if %errorlevel% equ 0 (
    goto :env_error_empty
)

REM Verifica se POSTGRES_PASSWORD esta vazio (ex: "POSTGRES_PASSWORD=")
findstr /r /c:"^POSTGRES_PASSWORD=$" ".env" >nul
if %errorlevel% equ 0 (
    goto :env_error_empty
)

echo [OK] Credenciais de seguranca parecem estar preenchidas.
echo.
goto :setup_venv


:env_error_empty
echo [ERRO] Credenciais de seguranca nao configuradas no arquivo .env.
echo [INFO] Por favor, abra o arquivo .env e configure sua GEMINI_API_KEY e seu POSTGRES_PASSWORD.
echo [INFO] Esses campos nao podem ficar vazios.
pause
exit /b 1


:setup_venv
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