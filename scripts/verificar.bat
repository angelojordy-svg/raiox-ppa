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
"%PY%" -m ruff check src tests
if errorlevel 1 exit /b %errorlevel%
"%PY%" -m pytest -q
exit /b %errorlevel%
