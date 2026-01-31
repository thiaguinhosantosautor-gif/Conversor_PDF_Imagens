@echo off
TITLE Conversor de PDF Web

REM Navega para o diretório da aplicação web
cd web_converter

REM Verifica se o Python está no PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python nao encontrado. Por favor, instale Python ou adicione-o ao PATH.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Inicia o servidor Flask em segundo plano
start /B python app.py

echo.
echo Servidor Flask iniciado. Aguardando alguns segundos para inicializacao...
ping 127.0.0.1 -n 5 > nul

REM Abre o navegador padrao na URL da aplicacao
start "" "http://127.0.0.1:5000/"

echo.
echo Aplicacao aberta no navegador. Voce pode fechar esta janela.
exit /b 0
