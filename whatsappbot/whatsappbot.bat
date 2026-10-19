@echo off
REM Atalho para Windows: executa o robo usando o Python do PATH (ou do venv ativo).
cd /d "%~dp0"
python whatsappbot.py %*
pause
