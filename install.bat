@echo off
:: Простой установщик для Windows
:: Просто запустите этот файл двойным кликом

set "VENV=venv"
set "REQUIREMENTS=requirements.txt"
set "MAIN_SCRIPT=main.py"
chcp 1251 > nul

echo "Проверяем Python..."
python --version >nul 2>&1
if errorlevel 1 (
    echo "ОШИБКА: Python не установлен или не в PATH"
    echo.
    echo "1. Скачайте с python.org/downloads/"
    echo "2. При установке отметьте [X] 'Add Python to PATH'"
    pause
    exit /b
)

echo "Создаем виртуальное окружение..."
python -m venv "%VENV%"
if errorlevel 1 (
    echo "ОШИБКА: Не удалось создать окружение"
    echo "Попробуйте удалить папку %VENV%"
    pause
    exit /b
)

echo "Устанавливаем зависимости..."
call "%VENV%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo "ОШИБКА: Проблемы с зависимостями"
    echo "Проверьте файл %REQUIREMENTS%"
    pause
    exit /b
)