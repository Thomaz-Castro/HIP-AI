@echo off
echo ========================================
echo 🏥 Sistema Médico - Iniciando...
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! 
    echo 📥 Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verifica se o arquivo .env existe
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado!
    echo 📋 Copie .env.example para .env e configure sua conexão MongoDB
    echo.
    echo Quer criar um .env básico agora? (s/n)
    set /p create_env=
    if /i "%create_env%"=="s" (
        copy .env.example .env
        echo ✅ Arquivo .env criado! Edite-o com suas credenciais do MongoDB Atlas
        notepad .env
    )
    pause
    exit /b 1
)

REM Instala dependências se necessário
if not exist "venv\" (
    echo 🔧 Criando ambiente virtual...
    python -m venv venv
)

echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo 📦 Instalando/atualizando dependências...
pip install -r requirements.txt --quiet

echo 🚀 Iniciando Sistema Médico...
echo.
python medical_system.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao executar o sistema!
    echo 💡 Verifique:
    echo   1. Configuração do MongoDB no arquivo .env
    echo   2. Conexão com internet
    echo   3. Credenciais do MongoDB Atlas
    echo.
)

pause