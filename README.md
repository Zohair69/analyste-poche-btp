# Analyste de poche BTP

Application qui permet à un artisan ou une petite entreprise du bâtiment de poser des questions en français sur ses données (devis, chantiers, factures, achats, heures) et d'obtenir une réponse chiffrée, un graphique et la requête SQL utilisée.

> Projet en cours de construction.

## Stack
Python · Streamlit · SQLite · API Claude (Anthropic) · Plotly · pytest

## Installation (Windows, avec Anaconda Prompt)
```bash
conda create -n btp python=3.11 -y
conda activate btp
pip install -r requirements.txt
copy .env.example .env   # puis coller sa clé API dans .env
streamlit run app.py
```

## Auteur
Zohair
