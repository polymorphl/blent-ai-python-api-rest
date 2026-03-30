# DigiMarket API

Une API REST utilisant le framework Flask, SQLAlchemy pour l'ORM et une base de donnée SQLite.

## Installation

0. Créer un environement virtuel et l'activer

- `cd blent-ai-python-api-rest`
- `python3 -m venv venv`
- `python3 venv/bin/activate`

1. Lancer la commande suivante pour récupérer les dépendances du projet : `pip3 install -r requirements.txt`

2. Créer un .env et remplir les valeurs nécéssaire au fonctionement de l'API

- `cp .env.example .env`
- Remplir les valeurs dans le fichier `.env`

# Utilisation

Pour démarrer le serveur Flask, on utilisera cette commande : `flask --app src run`

## Tests
Pour lancer les tests :

```bash
pytest
```

# Routes API

## Auth
- POST - `/api/auth/register`
- POST - `/api/auth/login`