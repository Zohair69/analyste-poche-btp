@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo A lancer depuis Anaconda Prompt.
echo === 1. Creation de l'environnement conda "btp" ===
call conda create -n btp python=3.11 -y
call conda activate btp
echo === 2. Installation des bibliotheques ===
pip install -r requirements.txt
echo === Termine. ===
pause
