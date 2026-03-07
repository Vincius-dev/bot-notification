@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: =============================================================================
:: dev.bat — Utilitários de desenvolvimento
:: =============================================================================

:MENU
cls
echo.
echo ========================================
echo    Bot Notification — Dev Utils
echo ========================================
echo   1. Criar ambiente virtual e instalar dependencias
echo   2. Subir MongoDB local (Docker)
echo   3. Criar colecoes e indices no banco local
echo   4. Executar testes
echo   5. Subir aplicacao completa (Docker Compose)
echo   6. Derrubar containers
echo   7. Construir imagem Docker de producao
echo   0. Sair
echo ========================================
set /p opcao="Escolha uma opcao: "

if "%opcao%"=="1" goto VENV
if "%opcao%"=="2" goto MONGO_UP
if "%opcao%"=="3" goto SEED
if "%opcao%"=="4" goto TESTS
if "%opcao%"=="5" goto COMPOSE_UP
if "%opcao%"=="6" goto COMPOSE_DOWN
if "%opcao%"=="7" goto BUILD_PROD
if "%opcao%"=="0" goto SAIR

echo Opcao invalida.
pause
goto MENU

:: -----------------------------------------------------------------------------
:VENV
echo.
echo ^>^> Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate.bat
echo ^>^> Instalando dependencias...
pip install -r requirements.txt
echo ^>^> Pronto! O venv ja esta ativado nesta sessao.
pause
goto MENU

:: -----------------------------------------------------------------------------
:MONGO_UP
echo.
echo ^>^> Subindo MongoDB local...
docker compose up mongo -d
echo ^>^> MongoDB disponivel em localhost:27017
pause
goto MENU

:: -----------------------------------------------------------------------------
:SEED
echo.
if not exist venv\Scripts\activate.bat (
    echo Venv nao encontrado. Execute a opcao 1 primeiro.
    pause
    goto MENU
)
call venv\Scripts\activate.bat
echo ^>^> Criando colecoes e indices no banco local...
python scripts\seed_dev_db.py
pause
goto MENU

:: -----------------------------------------------------------------------------
:TESTS
echo.
if not exist venv\Scripts\activate.bat (
    echo Venv nao encontrado. Execute a opcao 1 primeiro.
    pause
    goto MENU
)
call venv\Scripts\activate.bat
echo ^>^> Executando testes...
pytest
pause
goto MENU

:: -----------------------------------------------------------------------------
:COMPOSE_UP
echo.
echo ^>^> Criando volume de assets (se nao existir)...
docker volume create assets_dev
echo ^>^> Subindo aplicacao completa via Docker Compose...
docker compose up -d
echo ^>^> Containers rodando. Acompanhe com: docker attach bot-notification-app
pause
goto MENU

:: -----------------------------------------------------------------------------
:COMPOSE_DOWN
echo.
echo ^>^> Derrubando containers...
docker compose down
pause
goto MENU

:: -----------------------------------------------------------------------------
:BUILD_PROD
echo.
set /p versao="Informe a versao da imagem (ex: 1.0.0): "
if "%versao%"=="" (
    echo Versao nao informada. Operacao cancelada.
    pause
    goto MENU
)
echo ^>^> Construindo imagem bot-notif:%versao%...
docker build -t "bot-notif:%versao%" .
echo ^>^> Imagem criada: bot-notif:%versao%
pause
goto MENU

:: -----------------------------------------------------------------------------
:SAIR
echo Saindo...
endlocal
exit /b 0
