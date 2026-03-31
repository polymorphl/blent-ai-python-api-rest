# DigiMarket API

Une API REST utilisant le framework Flask, SQLAlchemy pour l'ORM et une base de donnée SQLite.

## Installation

0. Créer un environement virtuel et l'activer

- `cd blent-ai-python-api-rest`
- `python3 -m venv venv`
- `source venv/bin/activate`

1. Lancer la commande suivante pour récupérer les dépendances du projet : `pip3 install -r requirements.txt`

2. Créer un .env et remplir les valeurs nécéssaire au fonctionement de l'API

- `cp .env.example .env`
- Remplir les valeurs dans le fichier `.env`

# Utilisation

3. Initialiser la base de données et créer le compte administrateur :

```bash
python seed.py
```

> `seed.py` crée les tables (`db.create_all()`) puis insère l'admin. Il est idempotent : sans effet si l'admin existe déjà.

Identifiants administrateur créés :
- **Email** : `admin@digimarket.com`
- **Mot de passe** : `admin1234`

4. Démarrer le serveur :

```bash
flask --app src run
```

## Tests

Pour lancer les tests :

```bash
pytest
```

# Routes API

L'API suit une architecture **MVC** via les Blueprints Flask :

| Couche | Dossier | Rôle |
|---|---|---|
| **Model** | `src/models.py` | Définition des entités et accès aux données (SQLAlchemy) |
| **View** | `src/routes/` | Réception des requêtes HTTP, retour des réponses JSON |
| **Controller** | `src/controllers/` | Logique métier, validation |

## Auth
- POST - `/api/auth/register`
- POST - `/api/auth/login`

## Produits
- GET - `/api/produits` — Liste tous les produits (param optionnel : `?search=`)
- GET - `/api/produits/<id>` — Retourne un produit par son id
- POST - `/api/produits` — Crée un produit *(admin requis)*
- PUT - `/api/produits/<id>` — Met à jour un produit *(admin requis)*
- DELETE - `/api/produits/<id>` — Supprime un produit *(admin requis)*