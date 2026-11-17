@echo off
chcp 65001 >nul
set "PROJETO=%~dp0..\"
set "ENGINE=%~dp0..\..\..\..\Resumo PDF"
cd /d "%PROJETO%"
set "PYTHONPATH=%PROJETO%src;%PYTHONPATH%"
if exist "%PROJETO%.venv\Scripts\python.exe" (
  set "PY=%PROJETO%.venv\Scripts\python.exe"
) else (
  set "PY=%ENGINE%\.venv\Scripts\python.exe"
)
if not exist "%PY%" (
  echo ERRO: python nao encontrado. Crie .venv na pasta ou ajuste o caminho do motor.
  exit /b 2
)
set "ANO=%~1"
if "%ANO%"=="" set "ANO=2026"
echo ATENCAO: gere as 35 UGs somente depois de validar o prototipo.
"%PY%" -m pmp_raiox --ano %ANO% --todas
exit /b %errorlevel%
