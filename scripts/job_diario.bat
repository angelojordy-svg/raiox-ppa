@echo off
chcp 65001 >nul
set "DADOS=%~dp0..\..\..\_dados\Saida"
set "ANO=2026"
if exist "%DADOS%\despesas_programas_2027_*.xlsx" set "ANO=2027"
if exist "%DADOS%\despesas_programas_2028_*.xlsx" set "ANO=2028"
if exist "%DADOS%\despesas_programas_2029_*.xlsx" set "ANO=2029"
call "%~dp0gerar_tudo.bat" %ANO%
if errorlevel 1 exit /b %errorlevel%
call "%~dp0gerar_pdf.bat" %ANO%
if errorlevel 1 exit /b %errorlevel%
exit /b 0
