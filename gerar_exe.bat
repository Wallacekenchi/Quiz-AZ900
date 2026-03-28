@echo off
echo.
echo ==========================================
echo    GERANDO EXECUTAVEL: SIMULADO AZ-900
echo ==========================================
echo.

:: Ativando o Ambiente Virtual (venv)
call venv\Scripts\activate

:: Limpando pastas antigas para evitar erros de cache
if exist build rd /s /q build
if exist dist rd /s /q dist

:: Comando do PyInstaller com o ícone e arquivos de dados
pyinstaller --noconsole --onefile --icon=icone_az900.ico ^
 --name "Simulado_AZ900" ^
 --add-data "questions.txt;." ^
 --add-data "*.gif;." ^
 --add-data "*.jpg;." ^
 --add-data "*.png;." ^
 --add-data "*.mp3;." ^
 --add-data "*.wav;." ^
 main.py

echo.
echo ==========================================
echo    CONCLUIDO! O APP ESTA NA PASTA 'DIST'
echo ==========================================
pause