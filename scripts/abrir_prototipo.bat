@echo off
chcp 65001 >nul
set "SAIDA=%~dp0..\..\..\_dados\Saida\raiox"
if not exist "%SAIDA%\index.html" (
  echo Gere o prototipo primeiro: scripts\gerar_prototipo.bat
  exit /b 1
)
start "" "%SAIDA%\index.html"
exit /b 0
