@echo off
title Pet Desktop - Persona
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar a Persona.
    pause
)
