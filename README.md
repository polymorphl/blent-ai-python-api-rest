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

## Utilisation

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

## Architecture

L'API suit une architecture **MVC** via les Blueprints Flask :

| Couche | Dossier | Rôle |
|---|---|---|
| **Model** | `src/models.py` | Définition des entités et accès aux données (SQLAlchemy) |
| **View** | `src/routes/` | Réception des requêtes HTTP, retour des réponses JSON |
| **Controller** | `src/controllers/` | Logique métier, validation |

## Documentation de l'API

### Auth

#### `POST /api/auth/register`

Inscription d'un nouvel utilisateur. Le rôle est toujours `client`.

**Corps de la requête**

| Champ | Type | Requis | Description |
|---|---|---|---|
| `email` | string | oui | Adresse email unique |
| `password` | string | oui | Mot de passe |
| `name` | string | oui | Nom affiché |

**Réponse `201`**
```json
{ "message": "Utilisateur créé avec succès." }
```

---

#### `POST /api/auth/login`

Connexion et génération d'un token JWT.

**Corps de la requête**

| Champ | Type | Requis | Description |
|---|---|---|---|
| `email` | string | oui | Adresse email |
| `password` | string | oui | Mot de passe |

**Réponse `200`**
```json
{ "access_token": "<JWT>" }
```

---

### Produits

> Les routes `POST`, `PATCH` et `DELETE` sont réservées aux administrateurs (header `Authorization: Bearer <token>` requis).

#### `GET /api/produits`

Retourne la liste de tous les produits. Paramètre optionnel `?search=` pour filtrer par nom, catégorie ou description.

**Réponse `200`**
```json
{
  "products": [
    {
      "id": 1,
      "nom": "Clavier mécanique Cherry MX",
      "description": "Clavier gaming mécanique - switches Cherry MX Red",
      "categorie": "Périphériques",
      "prix": 89.99,
      "quantite_stock": 15,
      "date_creation": "2026-03-31T10:00:00"
    }
  ]
}
```

---

#### `GET /api/produits/<id>`

Retourne un produit par son identifiant.

**Réponse `200`** — même structure qu'un élément de la liste ci-dessus.

**Réponse `404`** — produit introuvable.

---

#### `POST /api/produits` *(admin)*

Crée un nouveau produit.

**Corps de la requête**

| Champ | Type | Requis | Description |
|---|---|---|---|
| `nom` | string | oui | Nom du produit |
| `categorie` | string | oui | Catégorie |
| `prix` | number | oui | Prix (> 0) |
| `description` | string | non | Description détaillée |
| `quantite_stock` | integer | non | Stock initial (défaut : 0) |

**Réponse `201`** — fiche complète du produit créé.

---

#### `PATCH /api/produits/<id>` *(admin)*

Met à jour un ou plusieurs champs d'un produit existant.

**Corps de la requête** — mêmes champs que `POST`, tous optionnels.

**Réponse `200`** — fiche complète du produit mis à jour.

**Réponse `404`** — produit introuvable.

---

#### `DELETE /api/produits/<id>` *(admin)*

Supprime un produit.

**Réponse `200`**
```json
{ "message": "Produit supprimé avec succès." }
```

**Réponse `404`** — produit introuvable.

---

### Commandes

> Toutes les routes nécessitent un token JWT (`Authorization: Bearer <token>`).

#### `GET /api/commandes`

Retourne les commandes. Un admin voit toutes les commandes, un client uniquement les siennes.

**Réponse `200`**
```json
{
  "orders": [
    {
      "id": 1,
      "utilisateur_id": 2,
      "date_commande": "2026-03-31T10:00:00",
      "adresse_livraison": "42 avenue de la Technologie, 75001 Paris",
      "statut": "en_attente",
      "lines_len": 2
    }
  ]
}
```

---

#### `GET /api/commandes/<id>`

Retourne une commande par son identifiant. Un client ne peut accéder qu'à ses propres commandes.

**Réponse `200`** — même structure qu'un élément de la liste ci-dessus.

**Réponse `403`** — accès refusé.

**Réponse `404`** — commande introuvable.

---

#### `POST /api/commandes`

Crée une nouvelle commande pour l'utilisateur connecté. Vérifie la disponibilité du stock et le décrémente à la validation.

**Corps de la requête**

| Champ | Type | Requis | Description |
|---|---|---|---|
| `adresse_livraison` | string | oui | Adresse de livraison |
| `lines` | array | oui | Liste des produits commandés |
| `lines[].produit_id` | integer | oui | Identifiant du produit |
| `lines[].quantite` | integer | oui | Quantité (> 0) |

**Réponse `201`** — fiche complète de la commande créée.

**Réponse `400`** — stock insuffisant ou champ manquant.

**Réponse `404`** — produit introuvable.

---

#### `PATCH /api/commandes/<id>` *(admin)*

Modifie le statut d'une commande.

**Corps de la requête**

| Champ | Type | Valeurs acceptées |
|---|---|---|
| `statut` | string | `en_attente`, `validée`, `expédiée`, `annulée` |

**Réponse `200`** — fiche complète de la commande mise à jour.

**Réponse `404`** — commande introuvable.

---

#### `GET /api/commandes/<id>/lignes`

Retourne les lignes d'une commande. Un client ne peut accéder qu'aux lignes de ses propres commandes.

**Réponse `200`**
```json
{
  "lines": [
    {
      "id": 1,
      "produit_id": 3,
      "nom_produit": "SSD Samsung 1 To",
      "quantite": 2,
      "prix_unitaire": 129.99
    }
  ]
}
```
**Réponse `403`** — accès refusé.

**Réponse `404`** — commande introuvable.