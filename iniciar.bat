@echo off
set "PROJECT_NAME=unibank"
set "PROJECT_ROOT=%USERPROFILE%\Desktop\%PROJECT_NAME%"
set "VENV_DIR=env"
set "APP_DIR=unibank_app"
set "RUNSERVER_URL=http://127.0.0.1:8000/"

echo.
echo =======================================================
echo === INICIALIZADOR DE PROJETO DJANGO (COMPLETO / LOG) ===
echo =======================================================

:: 1. Mudar para o diretorio raiz do projeto
echo.
echo [PASSO 1] Navegando para %PROJECT_ROOT%...
cd /d "%PROJECT_ROOT%"
if errorlevel 1 (
    echo ERRO CRITICO: Nao foi possivel encontrar o projeto.
    pause
    exit /b 1
)

:: 2. Verificar e Criar Ambiente Virtual (env)
echo.
echo [PASSO 2] Verificando Ambiente Virtual...
if not exist "%VENV_DIR%" (
    echo Ambiente virtual nao encontrado. Criando '%VENV_DIR%'...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERRO: Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
    echo Criacao de ambiente virtual concluida.
) else (
    echo Ambiente virtual '%VENV_DIR%' ja existe.
)

:: 3. Ativar o Ambiente Virtual
echo.
echo [PASSO 3] Ativando Ambiente Virtual...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERRO: Falha ao ativar o ambiente virtual.
    pause
    exit /b 1
)
echo Ambiente virtual ATIVADO.

:: 4. Mudar para a subpasta da aplicacao
echo.
echo [PASSO 4] Entrando na pasta de gerenciamento (%APP_DIR%)...
cd /d "%APP_DIR%"
if errorlevel 1 (
    echo ERRO CRITICO: Nao foi possivel encontrar a pasta %APP_DIR%.
    pause
    exit /b 1
)

:: 5. Instalar Requisitos
echo.
echo [PASSO 5] Instalando/Atualizando dependencias (requirements.txt)...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo AVISO: Falha na instalacao de dependencias. Prosseguindo...
    ) else (
        echo Instalacao de dependencias concluida.
    )
) else (
    echo ERRO CRITICO: requirements.txt nao encontrado em %CD%.
    pause
    exit /b 1
)

:: 6. Aplicar Migracoes
echo.
echo [PASSO 6] Verificando e aplicando migracoes...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo AVISO: Erro ao aplicar migracoes. Prosseguindo...
) else (
    echo Migracoes aplicadas com sucesso.
)

:: 7. Abrir Navegador e Iniciar o Servidor
echo.
echo =======================================================
echo [PASSO 7] Abrindo navegador e iniciando servidor...
echo O navegador padrao sera aberto em %RUNSERVER_URL%
echo Para parar o servidor, pressione Ctrl+C nesta janela.
echo =======================================================

:: Abrir Navegador Padrao
start "" "%RUNSERVER_URL%"

:: Iniciar o Servidor (bloqueia o prompt)
python manage.py runserver