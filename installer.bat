@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 1. Creation de l'environnement virtuel ===
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
echo === 2. Installation des bibliotheques ===
python -m pip install --upgrade pip
pip install -r requirements.txt
echo === 3. Premier commit Git ===
if not exist .git git init
git branch -M main
git add .
git commit -m "Initialisation du projet : structure, dependances, gitignore"
echo.
echo === Termine. Tu peux fermer cette fenetre. ===
pause
