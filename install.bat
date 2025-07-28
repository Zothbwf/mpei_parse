@echo off
:: ������� ���������� ��� Windows
:: ������ ��������� ���� ���� ������� ������

set "VENV=venv"
set "REQUIREMENTS=requirements.txt"
set "MAIN_SCRIPT=main.py"
chcp 1251 > nul

echo "��������� Python..."
python --version >nul 2>&1
if errorlevel 1 (
    echo "������: Python �� ���������� ��� �� � PATH"
    echo.
    echo "1. �������� � python.org/downloads/"
    echo "2. ��� ��������� �������� [X] 'Add Python to PATH'"
    pause
    exit /b
)

echo "������� ����������� ���������..."
python -m venv "%VENV%"
if errorlevel 1 (
    echo "������: �� ������� ������� ���������"
    echo "���������� ������� ����� %VENV%"
    pause
    exit /b
)

echo "������������� �����������..."
call "%VENV%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo "������: �������� � �������������"
    echo "��������� ���� %REQUIREMENTS%"
    pause
    exit /b
)