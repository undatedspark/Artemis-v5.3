@echo off
title ARTEMIS 5.3 - CORE INTERFACE
:: 1. Entra na pasta correta (ajuste se o caminho mudar)
cd /d "C:\Users\gabri\OneDrive\Desktop\ARTEMIS"

:: 2. Mata qualquer processo fantasma do Python para evitar o erro de CONFLICT
taskkill /F /IM python.exe /T >nul 2>&1

:: 3. Inicia o sistema pelo main.py para mostrar o banner gigante
python main.py

pause