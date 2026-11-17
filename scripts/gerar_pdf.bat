@echo off
chcp 65001 >nul
set "PROJETO=%~dp0..\"
set "ENGINE=%~dp0..\..\..\..\Resumo PDF"
set "SAIDA=%~dp0..\..\..\_dados\Saida\raiox"
cd /d "%PROJETO%"
if exist "%PROJETO%.venv\Scripts\python.exe" (
  set "PY=%PROJETO%.venv\Scripts\python.exe"
) else (
  set "PY=%ENGINE%\.venv\Scripts\python.exe"
)
if not exist "%PY%" (
  echo ERRO: python nao encontrado.
  exit /b 2
)
set "ANO=%~1"
set "BASE=%SAIDA%"
if not "%ANO%"=="" set "BASE=%SAIDA%\%ANO%"
"%PY%" "%~dp0gerar_pdf.py" --saida "%BASE%" --pdf "%BASE%\pdf"
exit /b %errorlevel%
