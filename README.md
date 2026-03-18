# HBnB — Holberton AirBnB Clone

Projet backend RESTful développé en Python/Flask dans le cadre du cursus Holberton School.
Reproduction partielle d'AirBnB : gestion des utilisateurs, lieux, équipements et avis, avec authentification JWT et persistence SQLAlchemy.

---

## Table des matières

1. [Architecture générale](#1-architecture-générale)
2. [Arborescence complète](#2-arborescence-complète)
3. [Fichiers racine](#3-fichiers-racine)
4. [Configuration — `config.py`](#4-configuration--configpy)
5. [Point d'entrée de l'application — `app/__init__.py`](#5-point-dentrée-de-lapplication--app__init__py)
6. [Modèles de données](#6-modèles-de-données)
7. [Couche API — `app/api/v1/`](#7-couche-api--appapiv1)
8. [Couche service — `app/services/`](#8-couche-service--appservices)
9. [Couche persistence — `app/persistence/`](#9-couche-persistence--apppersistence)
10. [Tests — `app/tests/`](#10-tests--apptests)
11. [Flux d'une requête de bout en bout](#11-flux-dune-requête-de-bout-en-bout)
12. [Endpoints disponibles](#12-endpoints-disponibles)
13. [Authentification JWT](#13-authentification-jwt)
14. [Démarrage rapide](#14-démarrage-rapide)
15. [Variables d'environnement](#15-variables-denvironnement)
16. [Évolution par partie](#16-évolution-par-partie)

---

## 1. Architecture générale

```
Client HTTP (curl / Postman / Frontend)
         │
         ▼
  ┌─────────────┐
  │   Flask App  │  ← run.py crée l'app via create_app()
  │  Flask-RESTX │  ← Swagger UI dispo sur /doc
  └──────┬──────┘
         │  Namespaces (users / places / amenities / reviews)
         ▼
  ┌─────────────────┐
  │   API Layer     │  ← app/api/v1/*.py
  │ (Resources REST)│  ← Validation, auth JWT, sérialisation JSON
  └──────┬──────────┘
         │  appels façade
         ▼
  ┌─────────────────┐
  │  Service Layer  │  ← app/services/facade.py
  │  (HBnBFacade)   │  ← Logique métier, validations transverses
  └──────┬──────────┘
         │  appels repository
         ▼
  ┌──────────────────────────┐
  │   Persistence Layer      │  ← app/persistence/repository.py
  │  InMemoryRepository      │  ← Stockage en mémoire (place/amenity/review)
  │  SQLAlchemyRepository    │  ← Stockage SQLite via SQLAlchemy (user)
  │  UserRepository          │  ← app/services/repositories/user_repository.py
  └──────┬───────────────────┘
         │
         ▼
  ┌─────────────┐
  │   Models    │  ← app/models/*.py
  │  (db.Model) │  ← BaseModel, User, Place, Amenity, Review
  └─────────────┘
         │
         ▼
  ┌─────────────────┐
  │  SQLite DB      │  ← development.db (auto-créée par db.create_all())
  └─────────────────┘
```

**Principe des couches :**

| Couche | Responsabilité | Ne doit PAS |
|--------|---------------|-------------|
| API | Recevoir HTTP, valider format, retourner JSON | Contenir de la logique métier |
| Service (Facade) | Orchestrer la logique, valider les règles métier | Connaître Flask ou SQLAlchemy |
| Repository | Accéder aux données | Contenir de la logique métier |
| Model | Définir la structure et les validations de base | Connaître les autres couches |

---

## 2. Arborescence complète

```
holbertonschool-hbnb/
├── README.md                          ← Ce fichier
└── part3/
    ├── run.py                         ← Point d'entrée (démarrage du serveur)
    ├── config.py                      ← Configurations Flask (dev/test/prod)
    ├── requirements.txt               ← Dépendances Python
    ├── __init__.py                    ← Rend part3 importable comme package
    ├── curl_commands.txt              ← Exemples de commandes curl de test
    ├── curl_tests.sh                  ← Script bash de tests curl automatisés
    ├── server.log                     ← Log du serveur (généré à l'exécution)
    └── app/
        ├── __init__.py                ← Factory create_app() + extensions Flask
        ├── config.py                  ← Alias de configuration (import depuis root)
        ├── models/
        │   ├── __init__.py
        │   ├── base_model.py          ← Classe mère SQLAlchemy (id, timestamps)
        │   ├── user.py                ← Modèle User (bcrypt, validations)
        │   ├── place.py               ← Modèle Place (géolocalisation, amenities)
        │   ├── amenity.py             ← Modèle Amenity (équipements)
        │   ├── review.py              ← Modèle Review (avis 1-5 étoiles)
        │   └── entities.py            ← Dataclasses légères (utilisées par facade)
        ├── api/
        │   ├── __init__.py
        │   ├── amenities.py           ← Namespace amenities (version non-versionée)
        │   └── v1/
        │       ├── __init__.py
        │       ├── users.py           ← Endpoints /api/v1/users + /login + /me
        │       ├── places.py          ← Endpoints /api/v1/places
        │       ├── amenities.py       ← Endpoints /api/v1/amenities
        │       └── reviews.py         ← Endpoints /api/v1/reviews
        ├── persistence/
        │   └── repository.py          ← Repository (InMemory + SQLAlchemy)
        ├── services/
        │   ├── __init__.py            ← Instancie facade (singleton)
        │   ├── facade.py              ← HBnBFacade : toute la logique métier
        │   └── repositories/
        │       ├── __init__.py
        │       └── user_repository.py ← UserRepository spécialisé
        └── tests/
            ├── test_models.py         ← Tests unitaires des modèles
            ├── test_api.py            ← Tests d'intégration API
            ├── test_amenities.py      ← Tests spécifiques amenities
            ├── test_endpoint.py       ← Tests des endpoints HTTP
            └── tests_report.md        ← Rapport des résultats de tests
```

---

## 3. Fichiers racine

### `part3/run.py`

**Rôle :** Point d'entrée unique pour démarrer le serveur Flask.

```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```

- Appelle `create_app()` avec la config `'development'` par défaut.
- `app.run(debug=True)` active le rechargement automatique en développement.
- En production, ce fichier est remplacé par un serveur WSGI (gunicorn, uWSGI).

**Commande :** `python run.py` ou `flask run`

---

### `part3/requirements.txt`

**Rôle :** Liste les dépendances Python du projet.

| Package | Version | Usage |
|---------|---------|-------|
| `flask` | latest | Framework web principal |
| `flask-restx` | latest | Extensions REST + Swagger UI auto |
| `flask-bcrypt` | latest | Hachage bcrypt des mots de passe |
| `flask-jwt-extended` | latest | Authentification JWT (tokens Bearer) |
| `flask-sqlalchemy` | latest | ORM SQLAlchemy pour Flask |

**Installation :** `pip install -r requirements.txt`

---

### `part3/config.py` (racine)

**Rôle :** Fichier de configuration à la racine (identique à `app/config.py`). Voir section [Configuration](#4-configuration--configpy).

---

### `part3/curl_commands.txt` et `part3/curl_tests.sh`

**Rôle :** Outils de test manuel de l'API.

- `curl_commands.txt` : recueil de commandes curl copiables-collables pour tester chaque endpoint.
- `curl_tests.sh` : script bash exécutable qui enchaîne les appels API et vérifie les réponses.

---

## 4. Configuration — `config.py`

**Chemin :** `part3/config.py` et `part3/app/config.py`

**Rôle :** Centralise toutes les configurations Flask selon l'environnement.

### Classes de configuration

```
Config (base)
├── DevelopmentConfig   ← utilisée par défaut
├── TestingConfig       ← utilisée dans les tests
└── ProductionConfig    ← utilisée en production
```

### Détail des classes

**`Config` (base commune)**
| Attribut | Valeur | Rôle |
|----------|--------|------|
| `SECRET_KEY` | `os.getenv('SECRET_KEY', 'default_secret_key')` | Clé de signature JWT et sessions Flask |
| `DEBUG` | `False` | Désactive le mode debug par défaut |
| `TESTING` | `False` | Désactive le mode test par défaut |

**`DevelopmentConfig`**
| Attribut | Valeur | Rôle |
|----------|--------|------|
| `DEBUG` | `True` | Rechargement automatique + traceback détaillé |
| `SQLALCHEMY_DATABASE_URI` | `'sqlite:///development.db'` | Base SQLite locale dans `part3/instance/` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Désactive les signaux SQLAlchemy (perf) |

**`TestingConfig`**
| Attribut | Valeur | Rôle |
|----------|--------|------|
| `TESTING` | `True` | Flask propage les exceptions dans les tests |
| `DEBUG` | `False` | Pas de rechargement automatique |

**`ProductionConfig`**
| Attribut | Valeur | Rôle |
|----------|--------|------|
| `DEBUG` | `False` | Jamais de debug en production |

**Dictionnaire de sélection :**
```python
config = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
```

---

## 5. Point d'entrée de l'application — `app/__init__.py`

**Rôle :** Factory function `create_app()` — crée et configure l'application Flask complète.

### Extensions instanciées (niveau module)

```python
bcrypt = Bcrypt()      # Hachage des mots de passe
jwt    = JWTManager()  # Gestion des tokens JWT
db     = SQLAlchemy()  # ORM base de données
```

Ces objets sont créés **sans app** (pattern Application Factory). Ils sont initialisés avec l'app dans `create_app()`.

### Ce que fait `create_app(config_name='development')`

1. **Crée l'app Flask** : `app = Flask(__name__)`
2. **Charge la config** : `app.config.from_object(config[config_name])`
3. **Configure JWT** : `app.config.setdefault('JWT_SECRET_KEY', ...)`
4. **Initialise les extensions** : `bcrypt.init_app(app)`, `jwt.init_app(app)`, `db.init_app(app)`
5. **Configure l'API REST** : `Api(app, version='1.0', title='HBnB API', doc='/doc')`
6. **Enregistre les namespaces** (imports paresseux pour éviter les imports circulaires) :
   - `/api/v1/users` → namespace users
   - `/api/v1/places` → namespace places
   - `/api/v1/amenities` → namespace amenities
   - `/api/v1/reviews` → namespace reviews

### Pourquoi les imports de namespaces sont dans `create_app()` ?

Pour éviter les **imports circulaires** :
- `users.py` importe `facade`
- `facade.py` importe `UserRepository`
- `user_repository.py` importe `User`
- `user.py` importe `db` depuis `app`

En retardant ces imports à l'intérieur de `create_app()`, on s'assure que `db` est déjà défini quand les modèles sont importés.

---

## 6. Modèles de données

### `app/models/base_model.py`

**Rôle :** Classe mère de tous les modèles SQLAlchemy. Fournit les champs communs et les méthodes de base.

**Héritage :** `db.Model` (SQLAlchemy)

**Attribut `__abstract__ = True`** : SQLAlchemy ne crée pas de table pour `BaseModel`, seulement pour ses sous-classes.

#### Colonnes

| Colonne | Type SQLAlchemy | Description |
|---------|----------------|-------------|
| `id` | `String(36)` PRIMARY KEY | UUID v4 généré automatiquement |
| `created_at` | `DateTime` | Date de création (auto) |
| `updated_at` | `DateTime` | Date de dernière modification (auto + `onupdate`) |

#### Méthodes

| Méthode | Signature | Description |
|---------|-----------|-------------|
| `save()` | `-> None` | Met à jour `updated_at` et commit la session SQLAlchemy |
| `update(data)` | `dict -> None` | Applique un dict de modifications et appelle `save()` |
| `to_dict()` | `-> dict` | Sérialise `id`, `created_at`, `updated_at` en JSON-compatible |

---

### `app/models/user.py`

**Rôle :** Modèle représentant un utilisateur de l'application.

**Héritage :** `BaseModel` → `db.Model`

**Table SQL :** `users`

#### Colonnes

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `first_name` | `String(50)` | NOT NULL | Prénom (max 50 chars) |
| `last_name` | `String(50)` | NOT NULL | Nom (max 50 chars) |
| `email` | `String(120)` | NOT NULL, UNIQUE | Email validé par regex |
| `password` | `String(128)` | NOT NULL | Hash bcrypt (jamais le mot de passe clair) |
| `is_admin` | `Boolean` | default=False | Droits administrateur |

#### Validations dans `__init__`

- `first_name` : requis, longueur ≤ 50
- `last_name` : requis, longueur ≤ 50
- `email` : requis, doit matcher `^[^@\s]+@[^@\s]+\.[^@\s]+$`
- `password` : requis (jamais stocké en clair)

#### Méthodes

| Méthode | Description |
|---------|-------------|
| `hash_password(password)` | Hache avec bcrypt et stocke dans `self.password` |
| `verify_password(password)` | Vérifie un mot de passe contre le hash stocké → `bool` |
| `password_hash` (property) | Alias de `self.password` pour compatibilité |
| `authenticate(password)` | Alias de `verify_password()` pour compatibilité |
| `update_profile(data)` | Met à jour `first_name`, `last_name`, `email` (filtrés) |
| `change_password(new_password)` | Re-hache et sauvegarde le nouveau mot de passe |
| `to_dict()` | Retourne les champs publics — **`password` volontairement absent** |

**Sécurité :** Le champ `password` n'apparaît jamais dans `to_dict()`. Aucun endpoint GET n'expose le hash.

---

### `app/models/place.py`

**Rôle :** Modèle représentant un lieu disponible à la location.

**Héritage :** `BaseModel`

> Note : `Place` n'a pas encore de colonne SQLAlchemy dans part3 — il utilise encore le stockage en mémoire via `InMemoryRepository`.

#### Attributs

| Attribut | Type Python | Contraintes | Description |
|----------|-------------|-------------|-------------|
| `title` | `str` | requis, max 100 | Titre du lieu |
| `description` | `str` | optionnel | Description libre |
| `price` | `float` | > 0 | Prix par nuit |
| `latitude` | `float` | -90.0 à 90.0 | Latitude géographique |
| `longitude` | `float` | -180.0 à 180.0 | Longitude géographique |
| `owner` | `User` | requis | Instance User (propriétaire) |
| `max_guests` | `int` | ≥ 1, default=1 | Capacité maximale |
| `is_available` | `bool` | default=True | Disponibilité |
| `reviews` | `list[Review]` | auto | Liste des avis associés |
| `amenities` | `list[Amenity]` | auto | Liste des équipements |

#### Méthodes

| Méthode | Description |
|---------|-------------|
| `update(data)` | Filtre sur les champs autorisés (pas `owner`) |
| `set_availability(status)` | Active/désactive le lieu |
| `add_amenity(amenity)` | Ajoute une Amenity si absente |
| `remove_amenity(amenity)` | Retire une Amenity |
| `add_review(review)` | Ajoute une Review (appelé par `Review.create()`) |
| `get_average_rating()` | Calcule la moyenne des notes → `float` (0.0 si vide) |
| `to_dict()` | Sérialise avec `owner_id`, listes d'ids (pas les objets) |

---

### `app/models/amenity.py`

**Rôle :** Modèle représentant un équipement (Wi-Fi, Parking, Piscine…).

**Héritage :** `BaseModel`

#### Attributs

| Attribut | Type | Contraintes | Description |
|----------|------|-------------|-------------|
| `name` | `str` | requis, max 50 | Nom de l'équipement |
| `description` | `str` | optionnel, default="" | Description optionnelle |

#### Méthodes

| Méthode | Description |
|---------|-------------|
| `update(data)` | Filtre sur `name` et `description` uniquement |
| `to_dict()` | Ajoute `name` et `description` au dict de base |

---

### `app/models/review.py`

**Rôle :** Modèle représentant un avis laissé par un User sur un Place.

**Héritage :** `BaseModel`

#### Attributs

| Attribut | Type | Contraintes | Description |
|----------|------|-------------|-------------|
| `rating` | `int` | 1 ≤ x ≤ 5 | Note de 1 à 5 étoiles |
| `comment` | `str` | requis | Texte de l'avis |
| `place` | `Place` | requis | Instance du lieu noté |
| `user` | `User` | requis | Instance de l'auteur |

#### Méthodes

| Méthode | Description |
|---------|-------------|
| `validate_rating(rating)` | Valide qu'un rating est un entier entre 1 et 5 |
| `update(data)` | Filtre sur `rating` et `comment` (place/user immuables) |
| `to_dict()` | Retourne `place_id` et `user_id` (pas les objets entiers) |

---

### `app/models/entities.py`

**Rôle :** Dataclasses légères (`@dataclass`) utilisées comme types de données simples par la facade. Ce sont des versions simplifiées des modèles principaux, sans SQLAlchemy.

**Contenu :** Redéfinit `User`, `Amenity`, `Place`, `Review` comme dataclasses avec validations `__post_init__`. Utilisé historiquement par `facade.py` pour les imports de type.

> Ces classes coexistent avec les modèles complets dans `models/` — la facade importe depuis ce fichier pour les annotations de type.

---

## 7. Couche API — `app/api/v1/`

Chaque fichier définit un **Namespace flask-restx** avec ses modèles de données (Swagger) et ses classes `Resource`.

### Architecture commune à tous les namespaces

```python
api = Namespace('name', description='...')

# Modèles Swagger (utilisés pour la validation et la doc)
model      = api.model(...)   # réponse
create_model = api.model(...) # création
update_model = api.model(...) # mise à jour

@api.route('/')
class List(Resource):
    def get(self):  ...   # liste
    def post(self): ...   # création

@api.route('/<id>')
class Item(Resource):
    def get(self, id):    ...  # lecture
    def put(self, id):    ...  # modification
    def delete(self, id): ...  # suppression (reviews seulement)
```

---

### `app/api/v1/users.py`

**Namespace :** `users` — monté sur `/api/v1/users`

#### Modèles Swagger

| Modèle | Champs | Usage |
|--------|--------|-------|
| `User` | id, email, first_name, last_name, is_admin, created_at, updated_at | Réponse (password absent) |
| `UserCreate` | email\*, password\*, first_name\*, last_name\* | Création |
| `UserUpdate` | first_name, last_name, password | Mise à jour |
| `UserLogin` | email\*, password\* | Authentification |

#### Endpoints

| Route | Méthode | Auth | Description |
|-------|---------|------|-------------|
| `/api/v1/users/` | GET | Non | Liste tous les utilisateurs |
| `/api/v1/users/` | POST | JWT optionnel | Crée un utilisateur (premier = admin auto) |
| `/api/v1/users/login` | POST | Non | Authentification → retourne JWT |
| `/api/v1/users/me` | GET | JWT requis | Retourne les infos du token courant |
| `/api/v1/users/<id>` | GET | Non | Détail d'un utilisateur |
| `/api/v1/users/<id>` | PUT | JWT + admin | Modifie un utilisateur |

#### Logique d'autorisation POST `/users/`

1. **Aucun utilisateur en base** → le premier créé devient admin automatiquement (bootstrap)
2. **JWT absent ou non-admin** → `403 Forbidden`
3. **Admin authentifié** → peut créer des utilisateurs avec ou sans `is_admin`

---

### `app/api/v1/places.py`

**Namespace :** `places` — monté sur `/api/v1/places`

#### Endpoints

| Route | Méthode | Auth | Description |
|-------|---------|------|-------------|
| `/api/v1/places/` | GET | Non | Liste simplifiée (id, title, lat, lng) |
| `/api/v1/places/` | POST | JWT requis | Crée un lieu (owner_id doit matcher l'utilisateur) |
| `/api/v1/places/<id>` | GET | Non | Détail complet (owner, amenities) |
| `/api/v1/places/<id>` | PUT | JWT requis | Modifie (owner ou admin uniquement) |

#### Règles métier

- Un utilisateur non-admin ne peut créer un lieu qu'avec son propre `owner_id`
- La modification est réservée au propriétaire ou à un admin
- Le GET détail retourne l'objet `owner` complet (first_name, last_name, email)

---

### `app/api/v1/amenities.py`

**Namespace :** `amenities` — monté sur `/api/v1/amenities`

#### Endpoints

| Route | Méthode | Auth | Description |
|-------|---------|------|-------------|
| `/api/v1/amenities/` | GET | Non | Liste toutes les amenities |
| `/api/v1/amenities/` | POST | JWT + admin | Crée une amenity |
| `/api/v1/amenities/<id>` | GET | Non | Détail d'une amenity |
| `/api/v1/amenities/<id>` | PUT | JWT + admin | Modifie une amenity |

**Restriction :** Seuls les admins peuvent créer et modifier des amenities.

---

### `app/api/v1/reviews.py`

**Namespace :** `reviews` — monté sur `/api/v1/reviews`

#### Endpoints

| Route | Méthode | Auth | Description |
|-------|---------|------|-------------|
| `/api/v1/reviews/` | GET | Non | Liste tous les avis |
| `/api/v1/reviews/` | POST | JWT requis | Crée un avis (user_id doit matcher) |
| `/api/v1/reviews/<id>` | GET | Non | Détail d'un avis |
| `/api/v1/reviews/<id>` | PUT | JWT requis | Modifie (auteur ou admin) |
| `/api/v1/reviews/<id>` | DELETE | JWT requis | Supprime (auteur ou admin) |
| `/api/v1/reviews/places/<place_id>/reviews` | GET | Non | Tous les avis d'un lieu |

**Note :** Reviews est le seul namespace avec un endpoint `DELETE`.

---

## 8. Couche service — `app/services/`

### `app/services/__init__.py`

**Rôle :** Instancie le singleton de la facade.

```python
from app.services.facade import HBnBFacade
facade = HBnBFacade()
```

Tous les namespaces API importent `from app.services import facade` pour accéder à la logique métier via ce singleton.

---

### `app/services/facade.py`

**Rôle :** Orchestrateur central de toute la logique métier. C'est **l'unique interface** entre la couche API et la couche persistence.

**Classe :** `HBnBFacade`

#### Repositories utilisés

| Attribut | Classe | Stockage |
|----------|--------|----------|
| `user_repo` | `UserRepository` | SQLite via SQLAlchemy |
| `place_repo` | `InMemoryRepository` | Mémoire RAM |
| `review_repo` | `InMemoryRepository` | Mémoire RAM |
| `amenity_repo` | `InMemoryRepository` | Mémoire RAM |

#### Méthodes — Users

| Méthode | Paramètres | Retour | Description |
|---------|------------|--------|-------------|
| `get_user(user_id)` | `str` | `User\|None` | Récupère par ID |
| `get_user_by_email(email)` | `str` | `User\|None` | Récupère par email |
| `get_users()` | — | `list[User]` | Tous les utilisateurs |
| `create_user(user_data)` | `dict` | `User` | Valide unicité email, crée et persiste |
| `update_user(user_id, data)` | `str, dict` | `User\|None` | Re-hache le password si fourni |

#### Méthodes — Places

| Méthode | Description |
|---------|-------------|
| `create_place(place_data)` | Résout `owner_id` → `User` et les IDs d'amenities → objets |
| `get_place(place_id)` | Récupère par ID |
| `get_all_places()` | Tous les lieux |
| `update_place(place_id, data)` | Mise à jour filtrée |

#### Méthodes — Amenities

| Méthode | Description |
|---------|-------------|
| `create_amenity(amenity_data)` | Crée et persiste |
| `get_amenity(amenity_id)` | Récupère par ID |
| `get_all_amenities()` | Toutes les amenities |
| `update_amenity(amenity_id, data)` | Mise à jour |

#### Méthodes — Reviews

| Méthode | Description |
|---------|-------------|
| `create_review(review_data)` | Résout `user_id` + `place_id`, valide existence |
| `get_review(review_id)` | Récupère par ID |
| `get_all_reviews()` | Tous les avis |
| `get_reviews_by_place(place_id)` | Filtre par lieu |
| `update_review(review_id, data)` | Mise à jour |
| `delete_review(review_id)` | Suppression |

---

### `app/services/repositories/user_repository.py`

**Rôle :** Repository spécialisé pour les utilisateurs. Étend `SQLAlchemyRepository` avec une méthode métier.

**Classe :** `UserRepository(SQLAlchemyRepository)`

| Méthode | Description |
|---------|-------------|
| `__init__()` | Appelle `super().__init__(User)` |
| `get_user_by_email(email)` | `User.query.filter_by(email=email).first()` |

---

## 9. Couche persistence — `app/persistence/repository.py`

**Rôle :** Définit le contrat (interface abstraite) et les deux implémentations concrètes.

### `Repository` (ABC)

Interface abstraite avec 7 méthodes obligatoires :

| Méthode | Description |
|---------|-------------|
| `add(obj)` | Persiste un objet |
| `get(obj_id)` | Récupère par ID |
| `get_all()` | Retourne tout |
| `update(obj_id, data)` | Mise à jour |
| `delete(obj_id)` | Suppression → `bool` |
| `get_by_attribute(attr_name, attr_value)` | Premier match sur un attribut |
| `get_all_by_attribute(attr_name, attr_value)` | Tous les matchs sur un attribut |

---

### `InMemoryRepository`

**Stockage :** `dict` Python `{ id: objet }`

**Usage :** Place, Amenity, Review (données non persistées entre redémarrages)

| Méthode | Implémentation |
|---------|---------------|
| `add(obj)` | `self._storage[obj.id] = obj` |
| `get(obj_id)` | `self._storage.get(obj_id)` |
| `get_all()` | `list(self._storage.values())` |
| `update(obj_id, data)` | Appelle `obj.update(data)` |
| `delete(obj_id)` | `del self._storage[obj_id]` |
| `get_by_attribute` | `next(filter(getattr == value), None)` |
| `get_all_by_attribute` | List comprehension sur `getattr` |

---

### `SQLAlchemyRepository`

**Stockage :** Base SQLite via SQLAlchemy ORM

**Usage :** User (données persistées dans `development.db`)

| Méthode | Implémentation SQLAlchemy |
|---------|--------------------------|
| `add(obj)` | `db.session.add(obj)` + `commit()` |
| `get(obj_id)` | `Model.query.get(obj_id)` |
| `get_all()` | `Model.query.all()` |
| `update(obj_id, data)` | `setattr` en boucle + `commit()` |
| `delete(obj_id)` | `db.session.delete(obj)` + `commit()` |
| `get_by_attribute` | `Model.query.filter_by(**{attr: val}).first()` |
| `get_all_by_attribute` | `Model.query.filter_by(**{attr: val}).all()` |

---

## 10. Tests — `app/tests/`

### `test_models.py`

Tests unitaires des modèles de données.

| Test | Ce qu'il vérifie |
|------|-----------------|
| Création valide | Les objets se créent sans erreur avec des données correctes |
| Validations | Les `ValueError` sont levées pour les données invalides |
| `to_dict()` | La sérialisation est correcte et complète |
| `hash_password` | Le hash bcrypt est différent du mot de passe en clair |
| `verify_password` | La vérification bcrypt fonctionne |

### `test_api.py`

Tests d'intégration de l'API via le client de test Flask.

| Test | Ce qu'il vérifie |
|------|-----------------|
| POST `/users/` | Création avec réponse 201, password absent de la réponse |
| GET `/users/<id>` | Récupération par ID |
| POST `/users/login` | Retourne un token JWT valide |
| Endpoints protégés | Retournent 401 sans token, 403 sans droits admin |

### `test_amenities.py`

Tests spécifiques aux amenities.

### `test_endpoint.py`

Tests HTTP bas niveau des endpoints (codes de statut, headers, format JSON).

### `tests_report.md`

Rapport markdown des résultats de tests (manuel ou généré).

---

## 11. Flux d'une requête de bout en bout

### Exemple : `POST /api/v1/users/login`

```
1. Client HTTP
   POST /api/v1/users/login
   Body: {"email": "john@test.com", "password": "secret"}

2. Flask routing
   → app/api/v1/users.py :: UserLogin.post()

3. Validation du payload
   → flask-restx vérifie la présence de email et password

4. Appel facade
   → facade.get_user_by_email("john@test.com")

5. UserRepository
   → User.query.filter_by(email="john@test.com").first()
   → Requête SQL : SELECT * FROM users WHERE email = 'john@test.com'

6. Vérification bcrypt
   → user.verify_password("secret")
   → bcrypt.check_password_hash(user.password, "secret") → True

7. Génération JWT
   → create_access_token(identity=user.id, additional_claims={id, is_admin})

8. Réponse
   → {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."} 200
```

### Exemple : `POST /api/v1/places/` (authentifié)

```
1. Client HTTP
   POST /api/v1/places/
   Headers: Authorization: Bearer <token>
   Body: {"title": "Maison", "price": 100, "latitude": 48.8, "longitude": 2.3,
          "owner_id": "<user_id>"}

2. Flask routing
   → app/api/v1/places.py :: PlaceList.post()

3. Vérification JWT
   → flask-jwt-extended décode le token → récupère user_id et is_admin

4. Contrôle d'autorisation
   → payload["owner_id"] == user_id ? Oui → continue

5. Appel facade
   → facade.create_place(place_data)

6. Facade résout les dépendances
   → facade.get_user(owner_id) → objet User
   → (pas d'amenities ici)

7. Création du modèle
   → Place(title, price, latitude, longitude, owner=user_obj)

8. Persistence
   → InMemoryRepository.add(place)
   → self._storage[place.id] = place

9. Réponse
   → {"id": "...", "title": "Maison", ...} 201
```

---

## 12. Endpoints disponibles

### Récapitulatif complet

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/doc` | Non | Interface Swagger UI |
| **Users** | | | |
| GET | `/api/v1/users/` | Non | Liste des utilisateurs |
| POST | `/api/v1/users/` | JWT optionnel | Créer un utilisateur |
| POST | `/api/v1/users/login` | Non | Obtenir un JWT |
| GET | `/api/v1/users/me` | JWT | Infos de l'utilisateur connecté |
| GET | `/api/v1/users/<id>` | Non | Détail d'un utilisateur |
| PUT | `/api/v1/users/<id>` | JWT + admin | Modifier un utilisateur |
| **Places** | | | |
| GET | `/api/v1/places/` | Non | Liste des lieux |
| POST | `/api/v1/places/` | JWT | Créer un lieu |
| GET | `/api/v1/places/<id>` | Non | Détail d'un lieu |
| PUT | `/api/v1/places/<id>` | JWT | Modifier un lieu |
| **Amenities** | | | |
| GET | `/api/v1/amenities/` | Non | Liste des équipements |
| POST | `/api/v1/amenities/` | JWT + admin | Créer un équipement |
| GET | `/api/v1/amenities/<id>` | Non | Détail d'un équipement |
| PUT | `/api/v1/amenities/<id>` | JWT + admin | Modifier un équipement |
| **Reviews** | | | |
| GET | `/api/v1/reviews/` | Non | Liste des avis |
| POST | `/api/v1/reviews/` | JWT | Créer un avis |
| GET | `/api/v1/reviews/<id>` | Non | Détail d'un avis |
| PUT | `/api/v1/reviews/<id>` | JWT | Modifier un avis |
| DELETE | `/api/v1/reviews/<id>` | JWT | Supprimer un avis |
| GET | `/api/v1/reviews/places/<place_id>/reviews` | Non | Avis d'un lieu |

---

## 13. Authentification JWT

### Fonctionnement

```
1. POST /api/v1/users/login  →  {"email": ..., "password": ...}
2. Réponse                   →  {"access_token": "eyJ..."}
3. Requêtes suivantes        →  Header: Authorization: Bearer eyJ...
4. Flask-JWT-Extended        →  Décode le token, injecte claims dans le contexte
```

### Claims stockés dans le token

```python
{
    "sub": "<user_id>",      # identité (get_jwt_identity())
    "id": "<user_id>",       # claim supplémentaire
    "is_admin": True|False   # claim supplémentaire
}
```

### Décorateurs utilisés

| Décorateur | Comportement |
|-----------|--------------|
| `@jwt_required()` | Retourne 401 si token absent ou invalide |
| `@jwt_required(optional=True)` | Passe sans token (claims vides) |
| `get_jwt()` | Retourne tous les claims du token |
| `get_jwt_identity()` | Retourne le `sub` (user_id) |

### Matrice des permissions

| Action | Non connecté | Utilisateur | Admin |
|--------|-------------|-------------|-------|
| Lire users/places/amenities/reviews | ✅ | ✅ | ✅ |
| Créer un lieu (son `owner_id`) | ❌ | ✅ | ✅ |
| Modifier son propre lieu | ❌ | ✅ | ✅ |
| Modifier le lieu d'un autre | ❌ | ❌ | ✅ |
| Créer/modifier des amenities | ❌ | ❌ | ✅ |
| Créer un utilisateur | ❌ | ❌ | ✅ |
| Modifier un utilisateur | ❌ | ❌ | ✅ |
| Créer/modifier sa review | ❌ | ✅ | ✅ |
| Supprimer la review d'un autre | ❌ | ❌ | ✅ |

---

## 14. Démarrage rapide

### Prérequis

```bash
python3 --version   # Python 3.10+
pip --version
```

### Installation

```bash
cd part3
pip install -r requirements.txt
```

### Initialisation de la base de données

```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

Cela crée `part3/instance/development.db` (SQLite).

### Démarrage du serveur

```bash
python run.py
# ou
flask run
```

Le serveur démarre sur `http://127.0.0.1:5000`

### Test rapide

```bash
# 1. Créer le premier utilisateur (devient admin automatiquement)
curl -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@test.com","password":"pass123"}'

# 2. Se connecter
curl -X POST http://127.0.0.1:5000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@test.com","password":"pass123"}'
# → {"access_token": "eyJ..."}

# 3. Utiliser le token
curl -X GET http://127.0.0.1:5000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."
```

### Swagger UI

Ouvrir `http://127.0.0.1:5000/doc` dans un navigateur pour accéder à la documentation interactive.

---

## 15. Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SECRET_KEY` | `'default_secret_key'` | Clé de signature JWT — **changer en prod** |
| `FLASK_ENV` | `development` | Environnement Flask |
| `FLASK_APP` | `run.py` | Point d'entrée pour `flask run` |

**Exemple `.env` :**
```bash
SECRET_KEY=une_cle_tres_longue_et_aleatoire_ici
FLASK_ENV=development
FLASK_APP=run.py
```

---

## 16. Évolution par partie

| Partie | Ajouts principaux |
|--------|------------------|
| **Part 1** | Modèles Python de base (`BaseModel`, `User`, `Place`, `Amenity`, `Review`) |
| **Part 2** | API REST Flask-RESTX, `InMemoryRepository`, `HBnBFacade`, Swagger UI |
| **Part 3** | Hash bcrypt des mots de passe, authentification JWT, contrôle d'accès par rôle |
| **Part 3.6** | SQLAlchemy + SQLite, `BaseModel` hérite de `db.Model`, `SQLAlchemyRepository`, `UserRepository`, `development.db` |

---

## Schéma des relations entre entités

```
User ──────────────── Place
 │   (owner 1→N)       │
 │                     │ (many-to-many)
 │                  Amenity
 │
 └──────────────── Review
      (author 1→N)    │
                      │ (belongs to)
                    Place
```

- Un **User** peut posséder plusieurs **Places**
- Un **User** peut écrire plusieurs **Reviews**
- Un **Place** peut avoir plusieurs **Reviews**
- Un **Place** peut avoir plusieurs **Amenities** (et vice-versa)
- Une **Review** appartient à exactement un **User** et un **Place**
