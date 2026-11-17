@echo off
chcp 65001 >nul
set "PROJETO=%~dp0..\"
set "ENGINE=%~dp0..\..\..\..\Resumo PDF"
cd /d "%PROJETO%"
set "PYTHONPATH=%PROJETO%src;%PYTHONPATH%"
if "%~1"=="" (
  echo uso: gerar_ano.bat 2027
  exit /b 2
)
if exist "%PROJETO%.venv\Scripts\python.exe" (
  set "PY=%PROJETO%.venv\Scripts\python.exe"
) else (
  set "PY=%ENGINE%\.venv\Scripts\python.exe"
)
if not exist "%PY%" (
  echo ERRO: python nao encontrado.
  exit /b 2
)
"%PY%" -m pmp_raiox --ano %1 --todas
exit /b %errorlevel%
